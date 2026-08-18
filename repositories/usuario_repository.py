"""Camada de acesso a dados de Usuario. Sem regras de negócio."""

from database import db
from models.usuario import Usuario


def listar_todos():
    return db.session.query(Usuario).order_by(Usuario.id).all()


def buscar_por_id(usuario_id):
    return db.session.get(Usuario, usuario_id)


def buscar_por_email(email):
    return db.session.query(Usuario).filter(Usuario.email == email).first()


def contar():
    return db.session.query(Usuario).count()


def salvar(usuario):
    db.session.add(usuario)
    db.session.commit()
    return usuario


def atualizar(usuario):
    db.session.commit()
    return usuario


def remover(usuario):
    db.session.delete(usuario)
    db.session.commit()
