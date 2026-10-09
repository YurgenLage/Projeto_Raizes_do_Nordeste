from sqlalchemy import Column, Integer, ForeignKey

from codigo.app.database import Base


class Fidelidade(Base):
    __tablename__ = "fidelidades"

    id_fidelidade = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        unique=True,
        nullable=False
    )
    pontos = Column(Integer, default=0, nullable=False)