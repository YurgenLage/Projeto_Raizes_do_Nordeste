from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from codigo.app.database import SessionLocal
from codigo.app.models.unidade import Unidade
from codigo.app.schemas.unidade import UnidadeCreate, UnidadeResponse
from codigo.app.auth import decodificar_token, verificar_perfil


router = APIRouter(
    prefix="/unidades",
    tags=["Unidades"]
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=UnidadeResponse, status_code=201)
def criar_unidade(
    unidade: UnidadeCreate,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    verificar_perfil(
        dados_token,
        ["GERENTE", "ADMIN"]
    )

    nova_unidade = Unidade(
        nome=unidade.nome,
        endereco=unidade.endereco,
        telefone=unidade.telefone
    )

    db.add(nova_unidade)
    db.commit()
    db.refresh(nova_unidade)

    return nova_unidade


@router.get("/", response_model=list[UnidadeResponse])
def listar_unidades(
    db: Session = Depends(get_db)
):
    unidades = db.query(Unidade).all()

    return unidades


@router.get("/{id_unidade}", response_model=UnidadeResponse)
def buscar_unidade(
    id_unidade: int,
    db: Session = Depends(get_db)
):
    unidade = (
        db.query(Unidade)
        .filter(Unidade.id_unidade == id_unidade)
        .first()
    )

    if unidade is None:
        raise HTTPException(
            status_code=404,
            detail="Unidade não encontrada"
        )

    return unidade