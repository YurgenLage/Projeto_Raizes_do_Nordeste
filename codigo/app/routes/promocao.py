from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from codigo.app.database import SessionLocal
from codigo.app.models.promocao import Promocao
from codigo.app.schemas.promocao import PromocaoCreate, PromocaoResponse
from codigo.app.auth import decodificar_token, verificar_perfil


router = APIRouter(
    prefix="/promocoes",
    tags=["Promoções"]
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PromocaoResponse, status_code=201)
def criar_promocao(
    promocao: PromocaoCreate,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    verificar_perfil(
        dados_token,
        ["GERENTE", "ADMIN"]
    )

    nova_promocao = Promocao(
        nome=promocao.nome,
        descricao=promocao.descricao,
        percentual_desconto=promocao.percentual_desconto,
        ativa=True
    )

    db.add(nova_promocao)
    db.commit()
    db.refresh(nova_promocao)

    return nova_promocao


@router.get("/", response_model=list[PromocaoResponse])
def listar_promocoes(
    db: Session = Depends(get_db)
):
    promocoes = (
        db.query(Promocao)
        .filter(Promocao.ativa == True)
        .all()
    )

    return promocoes