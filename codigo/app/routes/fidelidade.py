from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from codigo.app.database import SessionLocal
from codigo.app.models.fidelidade import Fidelidade
from codigo.app.schemas.fidelidade import FidelidadeResponse
from codigo.app.auth import decodificar_token


router = APIRouter(
    prefix="/fidelidades",
    tags=["Fidelidade"]
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/me", response_model=FidelidadeResponse)
def consultar_meus_pontos(
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    fidelidade = (
        db.query(Fidelidade)
        .filter(
            Fidelidade.id_usuario == dados_token["id_usuario"]
        )
        .first()
    )

    if fidelidade is None:
        fidelidade = Fidelidade(
            id_usuario=dados_token["id_usuario"],
            pontos=0
        )

        db.add(fidelidade)
        db.commit()
        db.refresh(fidelidade)

    return fidelidade