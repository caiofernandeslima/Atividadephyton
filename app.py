"""Ponto de entrada da aplicação HelpDesk (Flask + SQLAlchemy + SQLite)."""

import os

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from controllers.chamado_controller import chamado_bp, estatistica_bp
from controllers.usuario_controller import usuario_bp
from database import init_db
from services.exceptions import RegraDeNegocioError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "helpdesk.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.json.sort_keys = False

    init_db(app)

    app.register_blueprint(usuario_bp)
    app.register_blueprint(chamado_bp)
    app.register_blueprint(estatistica_bp)

    registrar_tratadores_de_erro(app)

    @app.get("/")
    def index():
        return jsonify(
            {
                "aplicacao": "API HelpDesk",
                "endpoints": [
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
                ],
            }
        ), 200

    return app


def registrar_tratadores_de_erro(app):
    """Converte exceções de negócio em respostas JSON com o código HTTP adequado."""

    @app.errorhandler(RegraDeNegocioError)
    def tratar_regra_de_negocio(erro):
        return jsonify({"erro": erro.mensagem}), erro.status_code

    @app.errorhandler(HTTPException)
    def tratar_http(erro):
        return jsonify({"erro": erro.description}), erro.code

    @app.errorhandler(Exception)
    def tratar_inesperado(erro):
        app.logger.exception(erro)
        return jsonify({"erro": "Erro interno no servidor."}), 500


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
