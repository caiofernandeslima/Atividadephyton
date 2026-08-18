"""Regras de negócio de Chamado."""

from models.chamado import Chamado
from repositories import chamado_repository, usuario_repository
from services.exceptions import ConflitoError, NaoEncontradoError, ValidacaoError

PRIORIDADES = ("Baixa", "Média", "Alta")

STATUS_ABERTO = "Aberto"
STATUS_EM_ATENDIMENTO = "Em atendimento"
STATUS_ENCERRADO = "Encerrado"
STATUS = (STATUS_ABERTO, STATUS_EM_ATENDIMENTO, STATUS_ENCERRADO)

# Transições permitidas: Aberto -> Em atendimento -> Encerrado
TRANSICOES_PERMITIDAS = {
    STATUS_ABERTO: (STATUS_EM_ATENDIMENTO,),
    STATUS_EM_ATENDIMENTO: (STATUS_ENCERRADO,),
    STATUS_ENCERRADO: (),
}

LIMITE_CHAMADOS_ALTA_ABERTOS = 5

TAMANHO_MINIMO_TITULO = 5
TAMANHO_MINIMO_DESCRICAO = 10


def _texto(valor):
    return valor.strip() if isinstance(valor, str) else valor


def _normalizar_prioridade(valor):
    """Aceita a prioridade sem diferenciar maiúsculas/minúsculas e a devolve canônica."""
    if not isinstance(valor, str):
        return None
    alvo = valor.strip().casefold()
    for prioridade in PRIORIDADES:
        if prioridade.casefold() == alvo:
            return prioridade
    return None


def _validar_titulo(titulo):
    # Título obrigatório
    if not titulo:
        raise ValidacaoError("O campo 'titulo' é obrigatório.")
    # Título deve possuir pelo menos 5 caracteres
    if len(titulo) < TAMANHO_MINIMO_TITULO:
        raise ValidacaoError(
            f"O campo 'titulo' deve possuir pelo menos {TAMANHO_MINIMO_TITULO} caracteres."
        )


def _validar_descricao(descricao):
    if not descricao:
        raise ValidacaoError("O campo 'descricao' é obrigatório.")
    # Descrição deve possuir pelo menos 10 caracteres
    if len(descricao) < TAMANHO_MINIMO_DESCRICAO:
        raise ValidacaoError(
            f"O campo 'descricao' deve possuir pelo menos {TAMANHO_MINIMO_DESCRICAO} caracteres."
        )


def _validar_limite_alta(usuario_id, prioridade, chamado_atual=None):
    """Um usuário não pode possuir mais de 5 chamados de prioridade Alta não encerrados."""
    if prioridade != "Alta":
        return

    total = chamado_repository.contar_por_usuario_prioridade_nao_encerrados(
        usuario_id, "Alta", STATUS_ENCERRADO
    )

    # Em uma atualização, o próprio chamado já pode estar contabilizado
    if (
        chamado_atual is not None
        and chamado_atual.usuario_id == usuario_id
        and chamado_atual.prioridade == "Alta"
        and chamado_atual.status != STATUS_ENCERRADO
    ):
        total -= 1

    if total >= LIMITE_CHAMADOS_ALTA_ABERTOS:
        raise ConflitoError(
            f"O usuário já possui {LIMITE_CHAMADOS_ALTA_ABERTOS} chamados de prioridade "
            "Alta não encerrados."
        )


def _obter_usuario(usuario_id):
    """O chamado deve obrigatoriamente estar vinculado a um usuário existente."""
    if usuario_id is None:
        raise ValidacaoError("O campo 'usuario_id' é obrigatório.")

    try:
        usuario_id = int(usuario_id)
    except (TypeError, ValueError):
        raise ValidacaoError("O campo 'usuario_id' deve ser um número inteiro.")

    usuario = usuario_repository.buscar_por_id(usuario_id)
    if usuario is None:
        raise ValidacaoError(f"Usuário {usuario_id} não encontrado.")
    return usuario


def listar_chamados():
    return chamado_repository.listar_todos()


def buscar_chamado(chamado_id):
    chamado = chamado_repository.buscar_por_id(chamado_id)
    if chamado is None:
        raise NaoEncontradoError(f"Chamado {chamado_id} não encontrado.")
    return chamado


def criar_chamado(dados):
    titulo = _texto(dados.get("titulo"))
    descricao = _texto(dados.get("descricao"))
    tecnico = _texto(dados.get("tecnico"))

    _validar_titulo(titulo)
    _validar_descricao(descricao)

    prioridade = _normalizar_prioridade(dados.get("prioridade"))
    if prioridade is None:
        raise ValidacaoError(
            "O campo 'prioridade' deve ser um dos valores: " + ", ".join(PRIORIDADES) + "."
        )

    usuario = _obter_usuario(dados.get("usuario_id"))
    _validar_limite_alta(usuario.id, prioridade)

    chamado = Chamado(
        titulo=titulo,
        descricao=descricao,
        prioridade=prioridade,
        status=STATUS_ABERTO,  # O status inicial deve ser "Aberto"
        tecnico=tecnico,
        usuario_id=usuario.id,
    )
    return chamado_repository.salvar(chamado)


def atualizar_chamado(chamado_id, dados):
    chamado = buscar_chamado(chamado_id)

    if "titulo" in dados:
        titulo = _texto(dados.get("titulo"))
        _validar_titulo(titulo)
        chamado.titulo = titulo

    if "descricao" in dados:
        descricao = _texto(dados.get("descricao"))
        _validar_descricao(descricao)
        chamado.descricao = descricao

    if "usuario_id" in dados:
        usuario = _obter_usuario(dados.get("usuario_id"))
        prioridade_alvo = _normalizar_prioridade(dados.get("prioridade")) or chamado.prioridade
        _validar_limite_alta(usuario.id, prioridade_alvo, chamado_atual=chamado)
        chamado.usuario_id = usuario.id

    if "prioridade" in dados:
        prioridade = _normalizar_prioridade(dados.get("prioridade"))
        if prioridade is None:
            raise ValidacaoError(
                "O campo 'prioridade' deve ser um dos valores: " + ", ".join(PRIORIDADES) + "."
            )
        _validar_limite_alta(chamado.usuario_id, prioridade, chamado_atual=chamado)
        chamado.prioridade = prioridade

    if "tecnico" in dados:
        chamado.tecnico = _texto(dados.get("tecnico"))

    # A mudança de status respeita as mesmas transições dos endpoints PATCH
    if "status" in dados:
        novo_status = _texto(dados.get("status"))
        _alterar_status(chamado, novo_status)

    return chamado_repository.atualizar(chamado)


def remover_chamado(chamado_id):
    chamado = buscar_chamado(chamado_id)
    chamado_repository.remover(chamado)


def _alterar_status(chamado, novo_status):
    if novo_status not in STATUS:
        raise ValidacaoError(
            "O campo 'status' deve ser um dos valores: " + ", ".join(STATUS) + "."
        )

    if novo_status == chamado.status:
        raise ConflitoError(f"O chamado já está com o status '{chamado.status}'.")

    if novo_status not in TRANSICOES_PERMITIDAS[chamado.status]:
        raise ConflitoError(
            f"Transição de status inválida: '{chamado.status}' → '{novo_status}'."
        )

    chamado.status = novo_status
    return chamado


def iniciar_atendimento(chamado_id):
    chamado = buscar_chamado(chamado_id)
    _alterar_status(chamado, STATUS_EM_ATENDIMENTO)
    return chamado_repository.atualizar(chamado)


def encerrar_chamado(chamado_id):
    chamado = buscar_chamado(chamado_id)
    _alterar_status(chamado, STATUS_ENCERRADO)
    return chamado_repository.atualizar(chamado)


def listar_abertos():
    return chamado_repository.listar_por_status(STATUS_ABERTO)


def listar_prioridade_alta():
    return chamado_repository.listar_por_prioridade("Alta")


def obter_estatisticas():
    return {
        "usuarios": usuario_repository.contar(),
        "chamados": chamado_repository.contar(),
        "abertos": chamado_repository.contar_por_status(STATUS_ABERTO),
        "em_atendimento": chamado_repository.contar_por_status(STATUS_EM_ATENDIMENTO),
        "encerrados": chamado_repository.contar_por_status(STATUS_ENCERRADO),
    }
