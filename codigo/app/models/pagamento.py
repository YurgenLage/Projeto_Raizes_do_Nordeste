from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

from codigo.app.database import Base


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id_pagamento = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(
        Integer,
        ForeignKey("pedidos.id_pedido"),
        nullable=False,
        unique=True
    )
    forma_pagamento = Column(String, nullable=False)
    status = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    codigo_transacao = Column(String, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow)