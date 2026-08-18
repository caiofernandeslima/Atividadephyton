"""Configuração da camada de persistência (SQLAlchemy + SQLite)."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Vincula o SQLAlchemy à aplicação Flask e cria as tabelas."""
    db.init_app(app)

    with app.app_context():
        # Importa os models para que sejam registrados no metadata antes do create_all
        from models import usuario, chamado  # noqa: F401

        db.create_all()
