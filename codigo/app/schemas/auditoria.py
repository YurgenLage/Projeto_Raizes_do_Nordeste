from pydantic import BaseModel
from datetime import datetime


class AuditoriaResponse(BaseModel):
    id_auditoria: int
    id_usuario: int | None
    acao: str
    entidade: str
    id_entidade: int | None
    detalhes: str | None
    criado_em: datetime

    class Config:
        from_attributes = True