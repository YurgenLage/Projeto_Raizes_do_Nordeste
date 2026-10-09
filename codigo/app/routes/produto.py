from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from codigo.app.database import SessionLocal
from codigo.app.models.produto import Produto
from codigo.app.models.estoque import Estoque
from codigo.app.models.unidade import Unidade

from codigo.app.schemas.produto import ProdutoCreate, ProdutoResponse
from codigo.app.auth import decodificar_token, verificar_perfil


router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ProdutoResponse, status_code=201)
def criar_produto(
    produto: ProdutoCreate,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    verificar_perfil(
        dados_token,
        ["GERENTE", "ADMIN"]
    )

    novo_produto = Produto(
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco
    )

    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)

    return novo_produto


@router.get("/cardapio/{id_unidade}", response_model=list[ProdutoResponse])
def listar_cardapio_unidade(
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

    if not unidade.ativo:
        raise HTTPException(
            status_code=400,
            detail="Unidade inativa"
        )

    produtos = (
        db.query(Produto)
        .join(
            Estoque,
            Estoque.id_produto == Produto.id_produto
        )
        .filter(
            Estoque.id_unidade == id_unidade,
            Estoque.quantidade > 0,
            Produto.ativo == True
        )
        .all()
    )

    return produtos


@router.get("/", response_model=list[ProdutoResponse])
def listar_produtos(
    db: Session = Depends(get_db)
):
    produtos = db.query(Produto).all()

    return produtos


@router.get("/{id_produto}", response_model=ProdutoResponse)
def buscar_produto(
    id_produto: int,
    db: Session = Depends(get_db)
):
    produto = (
        db.query(Produto)
        .filter(Produto.id_produto == id_produto)
        .first()
    )

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    return produto