from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from codigo.app.database import SessionLocal

from codigo.app.models.pedido import Pedido
from codigo.app.models.item_pedido import ItemPedido
from codigo.app.models.usuario import Usuario
from codigo.app.models.unidade import Unidade
from codigo.app.models.produto import Produto
from codigo.app.models.estoque import Estoque
from codigo.app.models.auditoria import Auditoria

from codigo.app.schemas.pedido import (
    PedidoCreate,
    PedidoResponse,
    PedidoStatusUpdate
)

from codigo.app.auth import decodificar_token, verificar_perfil


router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PedidoResponse, status_code=201)
def criar_pedido(
    pedido: PedidoCreate,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    id_usuario_token = dados_token["id_usuario"]

    if pedido.id_usuario != id_usuario_token:
        raise HTTPException(
            status_code=403,
            detail="Não é permitido criar pedido para outro usuário"
        )

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id_usuario == id_usuario_token)
        .first()
    )

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=403,
            detail="Usuário inativo"
        )

    unidade = (
        db.query(Unidade)
        .filter(Unidade.id_unidade == pedido.id_unidade)
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

    if len(pedido.itens) == 0:
        raise HTTPException(
            status_code=400,
            detail="O pedido deve possuir pelo menos um item"
        )

    valor_total = 0
    itens_validados = []

    for item in pedido.itens:

        if item.quantidade <= 0:
            raise HTTPException(
                status_code=400,
                detail="A quantidade deve ser maior que zero"
            )

        produto = (
            db.query(Produto)
            .filter(Produto.id_produto == item.id_produto)
            .first()
        )

        if produto is None:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado"
            )

        if not produto.ativo:
            raise HTTPException(
                status_code=400,
                detail="Produto inativo"
            )

        estoque = (
            db.query(Estoque)
            .filter(
                Estoque.id_unidade == pedido.id_unidade,
                Estoque.id_produto == item.id_produto
            )
            .first()
        )

        if estoque is None:
            raise HTTPException(
                status_code=404,
                detail="Produto não possui estoque nesta unidade"
            )

        if item.quantidade > estoque.quantidade:
            raise HTTPException(
                status_code=409,
                detail="Estoque insuficiente"
            )

        subtotal = produto.preco * item.quantidade

        valor_total += subtotal

        itens_validados.append({
            "item": item,
            "produto": produto,
            "estoque": estoque,
            "subtotal": subtotal
        })

    novo_pedido = Pedido(
        id_usuario=id_usuario_token,
        id_unidade=pedido.id_unidade,
        canal_pedido=pedido.canal_pedido,
        status="AGUARDANDO_PAGAMENTO",
        valor_total=valor_total
    )

    db.add(novo_pedido)
    db.flush()

    registro_auditoria = Auditoria(
        id_usuario=id_usuario_token,
        acao="CRIAR_PEDIDO",
        entidade="PEDIDO",
        id_entidade=novo_pedido.id_pedido,
        detalhes=f"Pedido criado pelo canal {pedido.canal_pedido}"
    )

    db.add(registro_auditoria)

    for dados_item in itens_validados:

        item = dados_item["item"]
        produto = dados_item["produto"]
        estoque = dados_item["estoque"]
        subtotal = dados_item["subtotal"]

        novo_item = ItemPedido(
            id_pedido=novo_pedido.id_pedido,
            id_produto=produto.id_produto,
            quantidade=item.quantidade,
            preco_unitario=produto.preco,
            subtotal=subtotal
        )

        db.add(novo_item)

        estoque.quantidade -= item.quantidade

    db.commit()
    db.refresh(novo_pedido)

    return novo_pedido


@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos(
    canal_pedido: str | None = None,
    status: str | None = None,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    query = db.query(Pedido)

    if dados_token["perfil"] not in ["GERENTE", "ADMIN"]:
        query = query.filter(
            Pedido.id_usuario == dados_token["id_usuario"]
        )

    if canal_pedido:
        query = query.filter(
            Pedido.canal_pedido == canal_pedido.upper()
        )

    if status:
        query = query.filter(
            Pedido.status == status.upper()
        )

    pedidos = query.all()

    return pedidos


@router.get("/{id_pedido}", response_model=PedidoResponse)
def buscar_pedido(
    id_pedido: int,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    pedido = (
        db.query(Pedido)
        .filter(Pedido.id_pedido == id_pedido)
        .first()
    )

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    if (
        dados_token["perfil"] not in ["GERENTE", "ADMIN"]
        and pedido.id_usuario != dados_token["id_usuario"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para visualizar este pedido"
        )

    return pedido


@router.put("/{id_pedido}/status", response_model=PedidoResponse)
def atualizar_status_pedido(
    id_pedido: int,
    dados: PedidoStatusUpdate,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    verificar_perfil(
        dados_token,
        ["COZINHA", "GERENTE", "ADMIN"]
    )

    pedido = (
        db.query(Pedido)
        .filter(Pedido.id_pedido == id_pedido)
        .first()
    )

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    transicoes_permitidas = {
        "RECEBIDO": ["EM_PREPARO", "CANCELADO"],
        "EM_PREPARO": ["PRONTO", "CANCELADO"],
        "PRONTO": ["ENTREGUE", "CANCELADO"]
    }

    status_permitidos = transicoes_permitidas.get(
        pedido.status,
        []
    )

    if dados.status not in status_permitidos:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Não é possível alterar o pedido de "
                f"{pedido.status} para {dados.status}"
            )
        )

    status_anterior = pedido.status

    pedido.status = dados.status
    pedido.atualizado_em = datetime.utcnow()

    registro_auditoria = Auditoria(
        id_usuario=dados_token["id_usuario"],
        acao="ALTERAR_STATUS",
        entidade="PEDIDO",
        id_entidade=pedido.id_pedido,
        detalhes=f"Status alterado de {status_anterior} para {dados.status}"
    )

    db.add(registro_auditoria)

    db.commit()
    db.refresh(pedido)

    return pedido