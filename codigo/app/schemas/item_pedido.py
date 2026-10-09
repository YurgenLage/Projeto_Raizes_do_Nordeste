from pydantic import BaseModel


class ItemPedidoCreate(BaseModel):
    id_produto: int
    quantidade: int


class ItemPedidoResponse(BaseModel):
    id_item_pedido: int
    id_pedido: int
    id_produto: int
    quantidade: int
    preco_unitario: float
    subtotal: float

    class Config:
        from_attributes = True