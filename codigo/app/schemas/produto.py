from pydantic import BaseModel
from datetime import datetime


class ProdutoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    preco: float


class ProdutoResponse(BaseModel):
    id_produto: int
    nome: str
    descricao: str | None
    preco: float
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True