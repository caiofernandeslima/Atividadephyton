"""Configuração da camada de persistência usando SQLAlchemy e SQLite."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Conecta o SQLAlchemy à aplicação Flask e cria as tabelas."""
    db.init_app(app)

    with app.app_context():
        # Carrega os models antes da criação das tabelas.
        from models import usuario, chamado  # noqa: F401

        db.create_all()
