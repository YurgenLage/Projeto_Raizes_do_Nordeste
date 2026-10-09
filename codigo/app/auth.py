from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException
from dotenv import load_dotenv
import os


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def criar_token(dados: dict):
    dados_token = dados.copy()

    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    dados_token.update({"exp": expiracao})

    token = jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def decodificar_token(token: str):
    try:
        dados = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        id_usuario = dados.get("sub")
        perfil = dados.get("perfil")

        if id_usuario is None:
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

        return {
            "id_usuario": int(id_usuario),
            "perfil": perfil
        }

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        )


def verificar_perfil(
    dados_token: dict,
    perfis_permitidos: list[str]
):
    if dados_token["perfil"] not in perfis_permitidos:
        raise HTTPException(
            status_code=403,
            detail="Acesso não autorizado para este perfil"
        )

    return True