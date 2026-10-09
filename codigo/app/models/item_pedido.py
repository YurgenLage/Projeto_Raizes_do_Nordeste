from sqlalchemy import Column, Integer, Float, ForeignKey

from codigo.app.database import Base


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id_item_pedido = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    id_produto = Column(Integer, ForeignKey("produtos.id_produto"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)