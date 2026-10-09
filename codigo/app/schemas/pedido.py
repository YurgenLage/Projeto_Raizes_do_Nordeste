from pydantic import BaseModel
from datetime import datetime
from typing import Literal

from codigo.app.schemas.item_pedido import ItemPedidoCreate


class PedidoCreate(BaseModel):
    id_usuario: int
    id_unidade: int
    canal_pedido: Literal[
        "APP",
        "TOTEM",
        "BALCAO",
        "PICKUP",
        "WEB"
    ]
    itens: list[ItemPedidoCreate]


class PedidoStatusUpdate(BaseModel):
    status: Literal[
        "EM_PREPARO",
        "PRONTO",
        "ENTREGUE",
        "CANCELADO"
    ]


class PedidoResponse(BaseModel):
    id_pedido: int
    id_usuario: int
    id_unidade: int
    canal_pedido: str
    status: str
    valor_total: float
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True