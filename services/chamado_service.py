"""Regras de negócio relacionadas aos chamados."""

from models.chamado import Chamado
from repositories import chamado_repository, usuario_repository
from services.exceptions import ConflitoError, NaoEncontradoError, ValidacaoError

PRIORIDADES = ("Baixa", "Média", "Alta")

STATUS_ABERTO = "Aberto"
STATUS_EM_ATENDIMENTO = "Em atendimento"
STATUS_ENCERRADO = "Encerrado"

STATUS = (
    STATUS_ABERTO,
    STATUS_EM_ATENDIMENTO,
    STATUS_ENCERRADO,
)

# Define quais mudanças de status podem acontecer
TRANSICOES_PERMITIDAS = {
    STATUS_ABERTO: (STATUS_EM_ATENDIMENTO,),
    STATUS_EM_ATENDIMENTO: (STATUS_ENCERRADO,),
    STATUS_ENCERRADO: (),
}

LIMITE_CHAMADOS_ALTA_ABERTOS = 5

TAMANHO_MINIMO_TITULO = 5
TAMANHO_MINIMO_DESCRICAO = 10


def _texto(valor):
    if isinstance(valor, str):
        return valor.strip()
    return valor


def _normalizar_prioridade(valor):
    """Converte uma prioridade válida para o formato utilizado pelo sistema."""

    if not isinstance(valor, str):
        return None

    prioridade_recebida = valor.strip().casefold()

    for prioridade_disponivel in PRIORIDADES:
        if prioridade_disponivel.casefold() == prioridade_recebida:
            return prioridade_disponivel

    return None


def _validar_titulo(titulo):
    if not titulo:
        raise ValidacaoError("O campo 'titulo' é obrigatório.")

    if len(titulo) < TAMANHO_MINIMO_TITULO:
        raise ValidacaoError(
            f"O campo 'titulo' deve possuir pelo menos "
            f"{TAMANHO_MINIMO_TITULO} caracteres."
        )


def _validar_descricao(descricao):
    if not descricao:
        raise ValidacaoError("O campo 'descricao' é obrigatório.")

    if len(descricao) < TAMANHO_MINIMO_DESCRICAO:
        raise ValidacaoError(
            f"O campo 'descricao' deve possuir pelo menos "
            f"{TAMANHO_MINIMO_DESCRICAO} caracteres."
        )


def _validar_limite_alta(usuario_id, prioridade, chamado_atual=None):
    """Controla o limite de chamados de prioridade Alta."""

    if prioridade != "Alta":
        return

    quantidade = chamado_repository.contar_por_usuario_prioridade_nao_encerrados(
        usuario_id,
        "Alta",
        STATUS_ENCERRADO
    )

    if chamado_atual is not None:
        mesmo_usuario = chamado_atual.usuario_id == usuario_id
        prioridade_alta = chamado_atual.prioridade == "Alta"
        nao_encerrado = chamado_atual.status != STATUS_ENCERRADO

        if mesmo_usuario and prioridade_alta and nao_encerrado:
            quantidade -= 1

    if quantidade >= LIMITE_CHAMADOS_ALTA_ABERTOS:
        raise ConflitoError(
            f"O usuário já possui {LIMITE_CHAMADOS_ALTA_ABERTOS} chamados "
            "de prioridade Alta não encerrados."
        )


def _obter_usuario(usuario_id):
    """Busca e valida o usuário associado ao chamado."""

    if usuario_id is None:
        raise ValidacaoError("O campo 'usuario_id' é obrigatório.")

    try:
        id_usuario = int(usuario_id)
    except (TypeError, ValueError):
        raise ValidacaoError(
            "O campo 'usuario_id' deve ser um número inteiro."
        )

    usuario = usuario_repository.buscar_por_id(id_usuario)

    if usuario is None:
        raise ValidacaoError(f"Usuário {id_usuario} não encontrado.")

    return usuario


def listar_chamados():
    chamados = chamado_repository.listar_todos()
    return chamados


def buscar_chamado(chamado_id):
    chamado = chamado_repository.buscar_por_id(chamado_id)

    if chamado is None:
        raise NaoEncontradoError(
            f"Chamado {chamado_id} não encontrado."
        )

    return chamado


def criar_chamado(dados):
    titulo = _texto(dados.get("titulo"))
    descricao = _texto(dados.get("descricao"))
    tecnico = _texto(dados.get("tecnico"))

    _validar_titulo(titulo)
    _validar_descricao(descricao)

    prioridade = _normalizar_prioridade(dados.get("prioridade"))

    if prioridade is None:
        opcoes = ", ".join(PRIORIDADES)
        raise ValidacaoError(
            "O campo 'prioridade' deve ser um dos valores: "
            + opcoes
            + "."
        )

    usuario = _obter_usuario(dados.get("usuario_id"))

    _validar_limite_alta(
        usuario.id,
        prioridade
    )

    novo_chamado = Chamado(
        titulo=titulo,
        descricao=descricao,
        prioridade=prioridade,
        status=STATUS_ABERTO,
        tecnico=tecnico,
        usuario_id=usuario.id,
    )

    return chamado_repository.salvar(novo_chamado)


def atualizar_chamado(chamado_id, dados):
    chamado = buscar_chamado(chamado_id)

    if "titulo" in dados:
        novo_titulo = _texto(dados.get("titulo"))
        _validar_titulo(novo_titulo)
        chamado.titulo = novo_titulo

    if "descricao" in dados:
        nova_descricao = _texto(dados.get("descricao"))
        _validar_descricao(nova_descricao)
        chamado.descricao = nova_descricao

    if "usuario_id" in dados:
        novo_usuario = _obter_usuario(dados.get("usuario_id"))

        prioridade_alvo = (
            _normalizar_prioridade(dados.get("prioridade"))
            or chamado.prioridade
        )

        _validar_limite_alta(
            novo_usuario.id,
            prioridade_alvo,
            chamado_atual=chamado
        )

        chamado.usuario_id = novo_usuario.id

    if "prioridade" in dados:
        nova_prioridade = _normalizar_prioridade(
            dados.get("prioridade")
        )

        if nova_prioridade is None:
            opcoes = ", ".join(PRIORIDADES)

            raise ValidacaoError(
                "O campo 'prioridade' deve ser um dos valores: "
                + opcoes
                + "."
            )

        _validar_limite_alta(
            chamado.usuario_id,
            nova_prioridade,
            chamado_atual=chamado
        )

        chamado.prioridade = nova_prioridade

    if "tecnico" in dados:
        novo_tecnico = _texto(dados.get("tecnico"))
        chamado.tecnico = novo_tecnico

    if "status" in dados:
        novo_status = _texto(dados.get("status"))
        _alterar_status(chamado, novo_status)

    return chamado_repository.atualizar(chamado)


def remover_chamado(chamado_id):
    chamado = buscar_chamado(chamado_id)
    chamado_repository.remover(chamado)


def _alterar_status(chamado, novo_status):
    if novo_status not in STATUS:
        opcoes = ", ".join(STATUS)

        raise ValidacaoError(
            "O campo 'status' deve ser um dos valores: "
            + opcoes
            + "."
        )

    if chamado.status == novo_status:
        raise ConflitoError(
            f"O chamado já está com o status '{chamado.status}'."
        )

    status_permitidos = TRANSICOES_PERMITIDAS[chamado.status]

    if novo_status not in status_permitidos:
        raise ConflitoError(
            f"Transição de status inválida: "
            f"'{chamado.status}' → '{novo_status}'."
        )

    chamado.status = novo_status

    return chamado


def iniciar_atendimento(chamado_id):
    chamado = buscar_chamado(chamado_id)

    _alterar_status(
        chamado,
        STATUS_EM_ATENDIMENTO
    )

    return chamado_repository.atualizar(chamado)


def encerrar_chamado(chamado_id):
    chamado = buscar_chamado(chamado_id)

    _alterar_status(
        chamado,
        STATUS_ENCERRADO
    )

    return chamado_repository.atualizar(chamado)


def listar_abertos():
    chamados = chamado_repository.listar_por_status(
        STATUS_ABERTO
    )

    return chamados


def listar_prioridade_alta():
    chamados = chamado_repository.listar_por_prioridade(
        "Alta"
    )

    return chamados


def obter_estatisticas():
    estatisticas = {
        "usuarios": usuario_repository.contar(),
        "chamados": chamado_repository.contar(),
        "abertos": chamado_repository.contar_por_status(
            STATUS_ABERTO
        ),
        "em_atendimento": chamado_repository.contar_por_status(
            STATUS_EM_ATENDIMENTO
        ),
        "encerrados": chamado_repository.contar_por_status(
            STATUS_ENCERRADO
        ),
    }

    return estatisticas
