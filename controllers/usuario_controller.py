"""Controller responsável pelas requisições relacionadas aos usuários."""

from flask import Blueprint, jsonify, request

from services import usuario_service
from services.exceptions import ValidacaoError

usuario_bp = Blueprint(
    "usuarios",
    __name__,
    url_prefix="/usuarios"
)


def _corpo_json():
    corpo = request.get_json(silent=True)

    if not isinstance(corpo, dict):
        raise ValidacaoError(
            "O corpo da requisição deve ser um JSON válido."
        )

    return corpo


@usuario_bp.get("")
def listar():
    lista_usuarios = usuario_service.listar_usuarios()

    resultado = [
        usuario.to_dict()
        for usuario in lista_usuarios
    ]

    return jsonify(resultado), 200


@usuario_bp.get("/<int:usuario_id>")
def buscar(usuario_id):
    usuario = usuario_service.buscar_usuario(usuario_id)
    dados = usuario.to_dict()

    return jsonify(dados), 200


@usuario_bp.post("")
def criar():
    dados = _corpo_json()
    usuario = usuario_service.criar_usuario(dados)

    return jsonify(usuario.to_dict()), 201


@usuario_bp.put("/<int:usuario_id>")
def atualizar(usuario_id):
    dados = _corpo_json()

    usuario = usuario_service.atualizar_usuario(
        usuario_id,
        dados
    )

    return jsonify(usuario.to_dict()), 200


@usuario_bp.delete("/<int:usuario_id>")
def remover(usuario_id):
    usuario_service.remover_usuario(usuario_id)

    return "", 204


@usuario_bp.get("/<int:usuario_id>/chamados")
def listar_chamados(usuario_id):
    chamados = usuario_service.listar_chamados_do_usuario(
        usuario_id
    )

    resultado = [
        chamado.to_dict()
        for chamado in chamados
    ]

    return jsonify(resultado), 200
