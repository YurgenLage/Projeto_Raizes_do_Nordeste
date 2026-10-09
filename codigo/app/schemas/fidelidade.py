from pydantic import BaseModel


class FidelidadeResponse(BaseModel):
    id_fidelidade: int
    id_usuario: int
    pontos: int

    class Config:
        from_attributes = True