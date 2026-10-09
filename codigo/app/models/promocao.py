from sqlalchemy import Column, Integer, String, Float, Boolean

from codigo.app.database import Base


class Promocao(Base):
    __tablename__ = "promocoes"

    id_promocao = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nome = Column(
        String,
        nullable=False
    )

    descricao = Column(
        String,
        nullable=True
    )

    percentual_desconto = Column(
        Float,
        nullable=False
    )

    ativa = Column(
        Boolean,
        default=True
    )