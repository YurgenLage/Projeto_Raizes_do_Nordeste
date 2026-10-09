from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

from codigo.app.database import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_unidade = Column(Integer, ForeignKey("unidades.id_unidade"), nullable=False)
    canal_pedido = Column(String, nullable=False)
    status = Column(String, nullable=False, default="AGUARDANDO_PAGAMENTO")
    valor_total = Column(Float, nullable=False, default=0.0)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow)