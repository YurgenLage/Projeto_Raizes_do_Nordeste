from pydantic import BaseModel, Field


class PromocaoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    percentual_desconto: float = Field(
        gt=0,
        le=100
    )


class PromocaoResponse(BaseModel):
    id_promocao: int
    nome: str
    descricao: str | None
    percentual_desconto: float
    ativa: bool

    class Config:
        from_attributes = True