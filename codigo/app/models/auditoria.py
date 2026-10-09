from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from codigo.app.database import Base


class Auditoria(Base):
    __tablename__ = "auditorias"

    id_auditoria = Column(
        Integer,
        primary_key=True,
        index=True
    )

    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=True
    )

    acao = Column(
        String,
        nullable=False
    )

    entidade = Column(
        String,
        nullable=False
    )

    id_entidade = Column(
        Integer,
        nullable=True
    )

    detalhes = Column(
        String,
        nullable=True
    )

    criado_em = Column(
        DateTime,
        default=datetime.utcnow
    )