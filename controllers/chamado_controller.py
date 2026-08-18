"""Controller de Chamado: recebe requisições, valida o básico e devolve respostas."""

from flask import Blueprint, jsonify, request

from services import chamado_service
from services.exceptions import ValidacaoError

chamado_bp = Blueprint("chamados", __name__, url_prefix="/chamados")
estatistica_bp = Blueprint("estatisticas", __name__)


def _corpo_json():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ValidacaoError("O corpo da requisição deve ser um JSON válido.")
    return dados


@chamado_bp.get("")
def listar():
    chamados = chamado_service.listar_chamados()
    return jsonify([c.to_dict() for c in chamados]), 200


@chamado_bp.get("/abertos")
def listar_abertos():
    chamados = chamado_service.listar_abertos()
    return jsonify([c.to_dict() for c in chamados]), 200


@chamado_bp.get("/prioridade/alta")
def listar_prioridade_alta():
    chamados = chamado_service.listar_prioridade_alta()
    return jsonify([c.to_dict() for c in chamados]), 200


@chamado_bp.get("/<int:chamado_id>")
def buscar(chamado_id):
    chamado = chamado_service.buscar_chamado(chamado_id)
    return jsonify(chamado.to_dict()), 200


@chamado_bp.post("")
def criar():
    chamado = chamado_service.criar_chamado(_corpo_json())
    return jsonify(chamado.to_dict()), 201


@chamado_bp.put("/<int:chamado_id>")
def atualizar(chamado_id):
    chamado = chamado_service.atualizar_chamado(chamado_id, _corpo_json())
    return jsonify(chamado.to_dict()), 200


@chamado_bp.delete("/<int:chamado_id>")
def remover(chamado_id):
    chamado_service.remover_chamado(chamado_id)
    return "", 204


@chamado_bp.patch("/<int:chamado_id>/iniciar")
def iniciar(chamado_id):
    chamado = chamado_service.iniciar_atendimento(chamado_id)
    return jsonify(chamado.to_dict()), 200


@chamado_bp.patch("/<int:chamado_id>/encerrar")
def encerrar(chamado_id):
    chamado = chamado_service.encerrar_chamado(chamado_id)
    return jsonify(chamado.to_dict()), 200


@estatistica_bp.get("/estatisticas")
def estatisticas():
    return jsonify(chamado_service.obter_estatisticas()), 200
