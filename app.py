"""Arquivo principal da aplicação HelpDesk usando Flask, SQLAlchemy e SQLite."""

import os

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from controllers.chamado_controller import chamado_bp, estatistica_bp
from controllers.usuario_controller import usuario_bp
from database import init_db
from services.exceptions import RegraDeNegocioError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app():
    aplicacao = Flask(__name__)

    caminho_banco = os.path.join(BASE_DIR, "helpdesk.db")
    aplicacao.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + caminho_banco
    aplicacao.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    aplicacao.json.sort_keys = False

    init_db(aplicacao)

    aplicacao.register_blueprint(usuario_bp)
    aplicacao.register_blueprint(chamado_bp)
    aplicacao.register_blueprint(estatistica_bp)

    registrar_tratadores_de_erro(aplicacao)

    @aplicacao.get("/")
    def index():
        endpoints = [
            "GET    /usuarios",
            "GET    /usuarios/<id>",
            "POST   /usuarios",
            "PUT    /usuarios/<id>",
            "DELETE /usuarios/<id>",
            "GET    /usuarios/<id>/chamados",
            "GET    /chamados",
            "GET    /chamados/<id>",
            "POST   /chamados",
            "PUT    /chamados/<id>",
            "DELETE /chamados/<id>",
            "PATCH  /chamados/<id>/iniciar",
            "PATCH  /chamados/<id>/encerrar",
            "GET    /chamados/abertos",
            "GET    /chamados/prioridade/alta",
            "GET    /estatisticas",
        ]

        return jsonify({
            "aplicacao": "API HelpDesk",
            "endpoints": endpoints,
        }), 200

    return aplicacao


def registrar_tratadores_de_erro(aplicacao):
    """Configura as respostas JSON utilizadas quando ocorre algum erro."""

    @aplicacao.errorhandler(RegraDeNegocioError)
    def tratar_regra_de_negocio(erro):
        resposta = {"erro": erro.mensagem}
        return jsonify(resposta), erro.status_code

    @aplicacao.errorhandler(HTTPException)
    def tratar_http(erro):
        resposta = {"erro": erro.description}
        return jsonify(resposta), erro.code

    @aplicacao.errorhandler(Exception)
    def tratar_inesperado(erro):
        aplicacao.logger.exception(erro)
        return jsonify({"erro": "Erro interno no servidor."}), 500


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
