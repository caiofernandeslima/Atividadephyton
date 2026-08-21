"""Model responsável pela entidade Usuario."""

from database import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    setor = db.Column(
        db.String(80),
        nullable=True
    )

    # Relacionamento entre usuário e seus chamados
    chamados = db.relationship(
        "Chamado",
        back_populates="usuario",
        lazy="select"
    )

    def to_dict(self):
        dados = {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "setor": self.setor,
        }

        return dados
