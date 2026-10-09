from pydantic import BaseModel
from datetime import datetime


class EstoqueCreate(BaseModel):
    id_unidade: int
    id_produto: int
    quantidade: int
    estoque_minimo: int = 0


class EstoqueResponse(BaseModel):
    id_estoque: int
    id_unidade: int
    id_produto: int
    quantidade: int
    estoque_minimo: int
    atualizado_em: datetime

    class Config:
        from_attributes = True