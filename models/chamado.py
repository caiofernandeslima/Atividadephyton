"""Entidade Chamado."""

from datetime import datetime

from database import db


class Chamado(db.Model):
    __tablename__ = "chamados"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Aberto")
    tecnico = db.Column(db.String(120), nullable=True)
    data_abertura = db.Column(db.DateTime, nullable=False, default=datetime.now)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    # Cada chamado pertence a apenas um usuário
    usuario = db.relationship("Usuario", back_populates="chamados")

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "prioridade": self.prioridade,
            "status": self.status,
            "tecnico": self.tecnico,
            "data_abertura": self.data_abertura.isoformat() if self.data_abertura else None,
            "usuario_id": self.usuario_id,
        }
