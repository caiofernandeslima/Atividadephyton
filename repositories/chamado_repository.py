"""Camada de acesso a dados de Chamado. Sem regras de negócio."""

from database import db
from models.chamado import Chamado


def listar_todos():
    return db.session.query(Chamado).order_by(Chamado.id).all()


def buscar_por_id(chamado_id):
    return db.session.get(Chamado, chamado_id)


def listar_por_usuario(usuario_id):
    return (
        db.session.query(Chamado)
        .filter(Chamado.usuario_id == usuario_id)
        .order_by(Chamado.id)
        .all()
    )


def listar_por_status(status):
    return (
        db.session.query(Chamado)
        .filter(Chamado.status == status)
        .order_by(Chamado.id)
        .all()
    )


def listar_por_prioridade(prioridade):
    return (
        db.session.query(Chamado)
        .filter(Chamado.prioridade == prioridade)
        .order_by(Chamado.id)
        .all()
    )


def contar_por_usuario_prioridade_nao_encerrados(usuario_id, prioridade, status_encerrado):
    return (
        db.session.query(Chamado)
        .filter(
            Chamado.usuario_id == usuario_id,
            Chamado.prioridade == prioridade,
            Chamado.status != status_encerrado,
        )
        .count()
    )


def contar():
    return db.session.query(Chamado).count()


def contar_por_status(status):
    return db.session.query(Chamado).filter(Chamado.status == status).count()


def salvar(chamado):
    db.session.add(chamado)
    db.session.commit()
    return chamado


def atualizar(chamado):
    db.session.commit()
    return chamado


def remover(chamado):
    db.session.delete(chamado)
    db.session.commit()
