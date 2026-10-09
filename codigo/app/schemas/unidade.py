from pydantic import BaseModel
from datetime import datetime


class UnidadeCreate(BaseModel):
    nome: str
    endereco: str
    telefone: str | None = None


class UnidadeResponse(BaseModel):
    id_unidade: int
    nome: str
    endereco: str
    telefone: str | None
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True