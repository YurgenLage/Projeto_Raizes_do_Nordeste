from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime

from codigo.app.database import Base


class Estoque(Base):
    __tablename__ = "estoques"

    id_estoque = Column(Integer, primary_key=True, index=True)
    id_unidade = Column(Integer, ForeignKey("unidades.id_unidade"), nullable=False)
    id_produto = Column(Integer, ForeignKey("produtos.id_produto"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=0)
    atualizado_em = Column(DateTime, default=datetime.utcnow)