from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from codigo.app.database import Base


class Unidade(Base):
    __tablename__ = "unidades"

    id_unidade = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    endereco = Column(String, nullable=False)
    telefone = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)