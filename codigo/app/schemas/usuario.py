from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: str
    consentimento_dados: bool

    @field_validator("consentimento_dados")
    @classmethod
    def validar_consentimento(cls, valor):
        if valor is not True:
            raise ValueError("É necessário consentir com o tratamento dos dados")
        return valor


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResponse(BaseModel):
    id_usuario: int
    nome: str
    email: EmailStr
    perfil: str
    consentimento_dados: bool
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True