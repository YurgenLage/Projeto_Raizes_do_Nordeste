from pydantic import BaseModel
from datetime import datetime


class PagamentoCreate(BaseModel):
    id_pedido: int
    forma_pagamento: str
    resultado: str


class PagamentoResponse(BaseModel):
    id_pagamento: int
    id_pedido: int
    forma_pagamento: str
    status: str
    valor: float
    codigo_transacao: str | None
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True