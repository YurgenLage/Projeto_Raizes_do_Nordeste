from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from codigo.app.database import SessionLocal
from codigo.app.models.estoque import Estoque
from codigo.app.models.unidade import Unidade
from codigo.app.models.produto import Produto
from codigo.app.schemas.estoque import EstoqueCreate, EstoqueResponse
from codigo.app.auth import decodificar_token, verificar_perfil


router = APIRouter(
    prefix="/estoques",
    tags=["Estoque"]
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=EstoqueResponse, status_code=201)
def criar_estoque(
    estoque: EstoqueCreate,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    verificar_perfil(
        dados_token,
        ["GERENTE", "ADMIN"]
    )

    unidade = (
        db.query(Unidade)
        .filter(Unidade.id_unidade == estoque.id_unidade)
        .first()
    )

    if unidade is None:
        raise HTTPException(
            status_code=404,
            detail="Unidade não encontrada"
        )

    produto = (
        db.query(Produto)
        .filter(Produto.id_produto == estoque.id_produto)
        .first()
    )

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    estoque_existente = (
        db.query(Estoque)
        .filter(
            Estoque.id_unidade == estoque.id_unidade,
            Estoque.id_produto == estoque.id_produto
        )
        .first()
    )

    if estoque_existente:
        raise HTTPException(
            status_code=400,
            detail="Estoque já cadastrado para este produto nesta unidade"
        )

    novo_estoque = Estoque(
        id_unidade=estoque.id_unidade,
        id_produto=estoque.id_produto,
        quantidade=estoque.quantidade,
        estoque_minimo=estoque.estoque_minimo
    )

    db.add(novo_estoque)
    db.commit()
    db.refresh(novo_estoque)

    return novo_estoque


@router.get("/", response_model=list[EstoqueResponse])
def listar_estoques(
    db: Session = Depends(get_db)
):
    estoques = db.query(Estoque).all()

    return estoques


@router.get("/{id_estoque}", response_model=EstoqueResponse)
def buscar_estoque(
    id_estoque: int,
    db: Session = Depends(get_db)
):
    estoque = (
        db.query(Estoque)
        .filter(Estoque.id_estoque == id_estoque)
        .first()
    )

    if estoque is None:
        raise HTTPException(
            status_code=404,
            detail="Estoque não encontrado"
        )

    return estoque


@router.put("/{id_estoque}/entrada", response_model=EstoqueResponse)
def entrada_estoque(
    id_estoque: int,
    quantidade: int,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    verificar_perfil(
        dados_token,
        ["GERENTE", "ADMIN"]
    )

    estoque = (
        db.query(Estoque)
        .filter(Estoque.id_estoque == id_estoque)
        .first()
    )

    if estoque is None:
        raise HTTPException(
            status_code=404,
            detail="Estoque não encontrado"
        )

    if quantidade <= 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade deve ser maior que zero"
        )

    estoque.quantidade += quantidade

    db.commit()
    db.refresh(estoque)

    return estoque


@router.put("/{id_estoque}/saida", response_model=EstoqueResponse)
def saida_estoque(
    id_estoque: int,
    quantidade: int,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    verificar_perfil(
        dados_token,
        ["GERENTE", "ADMIN"]
    )

    estoque = (
        db.query(Estoque)
        .filter(Estoque.id_estoque == id_estoque)
        .first()
    )

    if estoque is None:
        raise HTTPException(
            status_code=404,
            detail="Estoque não encontrado"
        )

    if quantidade <= 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade deve ser maior que zero"
        )

    if quantidade > estoque.quantidade:
        raise HTTPException(
            status_code=409,
            detail="Estoque insuficiente"
        )

    estoque.quantidade -= quantidade

    db.commit()
    db.refresh(estoque)

    return estoque