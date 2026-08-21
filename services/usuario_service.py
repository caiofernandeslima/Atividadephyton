"""Regras de negócio relacionadas aos usuários."""

from models.usuario import Usuario
from repositories import chamado_repository, usuario_repository
from services.exceptions import ConflitoError, NaoEncontradoError, ValidacaoError


def _texto(valor):
    if isinstance(valor, str):
        return valor.strip()
    return valor


def listar_usuarios():
    usuarios = usuario_repository.listar_todos()
    return usuarios


def buscar_usuario(usuario_id):
    usuario_encontrado = usuario_repository.buscar_por_id(usuario_id)

    if usuario_encontrado is None:
        raise NaoEncontradoError(f"Usuário {usuario_id} não encontrado.")

    return usuario_encontrado


def criar_usuario(dados):
    nome = _texto(dados.get("nome"))
    email = _texto(dados.get("email"))
    setor = _texto(dados.get("setor"))

    # Verifica se o nome foi informado
    if not nome:
        raise ValidacaoError("O campo 'nome' é obrigatório.")

    # Verifica se o e-mail foi informado
    if not email:
        raise ValidacaoError("O campo 'email' é obrigatório.")

    # Evita cadastro de e-mails repetidos
    usuario_existente = usuario_repository.buscar_por_email(email)

    if usuario_existente is not None:
        raise ConflitoError(
            f"Já existe um usuário cadastrado com o e-mail '{email}'."
        )

    novo_usuario = Usuario(
        nome=nome,
        email=email,
        setor=setor
    )

    return usuario_repository.salvar(novo_usuario)


def atualizar_usuario(usuario_id, dados):
    usuario = buscar_usuario(usuario_id)

    if "nome" in dados:
        novo_nome = _texto(dados.get("nome"))

        if not novo_nome:
            raise ValidacaoError("O campo 'nome' é obrigatório.")

        usuario.nome = novo_nome

    if "email" in dados:
        novo_email = _texto(dados.get("email"))

        if not novo_email:
            raise ValidacaoError("O campo 'email' é obrigatório.")

        usuario_existente = usuario_repository.buscar_por_email(novo_email)

        if usuario_existente is not None and usuario_existente.id != usuario.id:
            raise ConflitoError(
                f"Já existe um usuário cadastrado com o e-mail '{novo_email}'."
            )

        usuario.email = novo_email

    if "setor" in dados:
        novo_setor = _texto(dados.get("setor"))
        usuario.setor = novo_setor

    return usuario_repository.atualizar(usuario)


def remover_usuario(usuario_id):
    usuario = buscar_usuario(usuario_id)

    chamados_usuario = chamado_repository.listar_por_usuario(usuario.id)

    # Usuários com chamados cadastrados não podem ser removidos
    if chamados_usuario:
        raise ConflitoError(
            "Não é possível excluir um usuário que possui chamados cadastrados."
        )

    usuario_repository.remover(usuario)


def listar_chamados_do_usuario(usuario_id):
    usuario = buscar_usuario(usuario_id)
    chamados = chamado_repository.listar_por_usuario(usuario.id)

    return chamados
