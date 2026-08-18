"""Regras de negócio de Usuario."""

from models.usuario import Usuario
from repositories import chamado_repository, usuario_repository
from services.exceptions import ConflitoError, NaoEncontradoError, ValidacaoError


def _texto(valor):
    return valor.strip() if isinstance(valor, str) else valor


def listar_usuarios():
    return usuario_repository.listar_todos()


def buscar_usuario(usuario_id):
    usuario = usuario_repository.buscar_por_id(usuario_id)
    if usuario is None:
        raise NaoEncontradoError(f"Usuário {usuario_id} não encontrado.")
    return usuario


def criar_usuario(dados):
    nome = _texto(dados.get("nome"))
    email = _texto(dados.get("email"))
    setor = _texto(dados.get("setor"))

    # Nome é obrigatório
    if not nome:
        raise ValidacaoError("O campo 'nome' é obrigatório.")

    # E-mail é obrigatório
    if not email:
        raise ValidacaoError("O campo 'email' é obrigatório.")

    # Não permitir dois usuários com o mesmo e-mail
    if usuario_repository.buscar_por_email(email) is not None:
        raise ConflitoError(f"Já existe um usuário cadastrado com o e-mail '{email}'.")

    usuario = Usuario(nome=nome, email=email, setor=setor)
    return usuario_repository.salvar(usuario)


def atualizar_usuario(usuario_id, dados):
    usuario = buscar_usuario(usuario_id)

    if "nome" in dados:
        nome = _texto(dados.get("nome"))
        if not nome:
            raise ValidacaoError("O campo 'nome' é obrigatório.")
        usuario.nome = nome

    if "email" in dados:
        email = _texto(dados.get("email"))
        if not email:
            raise ValidacaoError("O campo 'email' é obrigatório.")

        existente = usuario_repository.buscar_por_email(email)
        if existente is not None and existente.id != usuario.id:
            raise ConflitoError(f"Já existe um usuário cadastrado com o e-mail '{email}'.")
        usuario.email = email

    if "setor" in dados:
        usuario.setor = _texto(dados.get("setor"))

    return usuario_repository.atualizar(usuario)


def remover_usuario(usuario_id):
    usuario = buscar_usuario(usuario_id)

    # Não permitir excluir um usuário que possua chamados cadastrados
    if chamado_repository.listar_por_usuario(usuario.id):
        raise ConflitoError(
            "Não é possível excluir um usuário que possui chamados cadastrados."
        )

    usuario_repository.remover(usuario)


def listar_chamados_do_usuario(usuario_id):
    usuario = buscar_usuario(usuario_id)
    return chamado_repository.listar_por_usuario(usuario.id)
