from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from codigo.app.database import SessionLocal

from codigo.app.models.auditoria import Auditoria
from codigo.app.schemas.auditoria import AuditoriaResponse

from codigo.app.auth import decodificar_token, verificar_perfil


router = APIRouter(
    prefix="/auditorias",
    tags=["Auditoria"]
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[AuditoriaResponse])
def listar_auditorias(
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    verificar_perfil(
        dados_token,
        ["GERENTE", "ADMIN"]
    )

    auditorias = (
        db.query(Auditoria)
        .order_by(Auditoria.id_auditoria.desc())
        .all()
    )

    return auditorias