"""Controller de Usuario: recebe requisições, valida o básico e devolve respostas."""

from flask import Blueprint, jsonify, request

from services import usuario_service
from services.exceptions import ValidacaoError

usuario_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def _corpo_json():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ValidacaoError("O corpo da requisição deve ser um JSON válido.")
    return dados


@usuario_bp.get("")
def listar():
    usuarios = usuario_service.listar_usuarios()
    return jsonify([u.to_dict() for u in usuarios]), 200


@usuario_bp.get("/<int:usuario_id>")
def buscar(usuario_id):
    usuario = usuario_service.buscar_usuario(usuario_id)
    return jsonify(usuario.to_dict()), 200


@usuario_bp.post("")
def criar():
    usuario = usuario_service.criar_usuario(_corpo_json())
    return jsonify(usuario.to_dict()), 201


@usuario_bp.put("/<int:usuario_id>")
def atualizar(usuario_id):
    usuario = usuario_service.atualizar_usuario(usuario_id, _corpo_json())
    return jsonify(usuario.to_dict()), 200


@usuario_bp.delete("/<int:usuario_id>")
def remover(usuario_id):
    usuario_service.remover_usuario(usuario_id)
    return "", 204


@usuario_bp.get("/<int:usuario_id>/chamados")
def listar_chamados(usuario_id):
    chamados = usuario_service.listar_chamados_do_usuario(usuario_id)
    return jsonify([c.to_dict() for c in chamados]), 200
