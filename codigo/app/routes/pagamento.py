from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import uuid4

from codigo.app.database import SessionLocal

from codigo.app.models.pagamento import Pagamento
from codigo.app.models.pedido import Pedido
from codigo.app.models.item_pedido import ItemPedido
from codigo.app.models.estoque import Estoque
from codigo.app.models.auditoria import Auditoria
from codigo.app.models.fidelidade import Fidelidade

from codigo.app.schemas.pagamento import PagamentoCreate, PagamentoResponse
from codigo.app.auth import decodificar_token


router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"]
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PagamentoResponse, status_code=201)
def processar_pagamento(
    pagamento: PagamentoCreate,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    pedido = (
        db.query(Pedido)
        .filter(Pedido.id_pedido == pagamento.id_pedido)
        .first()
    )

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    if pedido.id_usuario != dados_token["id_usuario"]:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para pagar este pedido"
        )

    pagamento_existente = (
        db.query(Pagamento)
        .filter(Pagamento.id_pedido == pagamento.id_pedido)
        .first()
    )

    if pagamento_existente:
        raise HTTPException(
            status_code=409,
            detail="Este pedido já possui pagamento registrado"
        )

    resultado = pagamento.resultado.upper()

    if resultado not in ["APROVADO", "RECUSADO"]:
        raise HTTPException(
            status_code=400,
            detail="Resultado do pagamento deve ser APROVADO ou RECUSADO"
        )

    codigo_transacao = str(uuid4())

    novo_pagamento = Pagamento(
        id_pedido=pedido.id_pedido,
        forma_pagamento=pagamento.forma_pagamento,
        status=resultado,
        valor=pedido.valor_total,
        codigo_transacao=codigo_transacao
    )

    if resultado == "APROVADO":
        pedido.status = "RECEBIDO"

        fidelidade = (
            db.query(Fidelidade)
            .filter(
                Fidelidade.id_usuario == pedido.id_usuario
            )
            .first()
        )

        if fidelidade is None:
            fidelidade = Fidelidade(
                id_usuario=pedido.id_usuario,
                pontos=0
            )

            db.add(fidelidade)
            db.flush()

        pontos_ganhos = int(pedido.valor_total)

        fidelidade.pontos = (
            fidelidade.pontos + pontos_ganhos
        )

        db.add(fidelidade)

    else:
        pedido.status = "PAGAMENTO_RECUSADO"

        itens_pedido = (
            db.query(ItemPedido)
            .filter(ItemPedido.id_pedido == pedido.id_pedido)
            .all()
        )

        if len(itens_pedido) == 0:
            raise HTTPException(
                status_code=404,
                detail="Itens do pedido não encontrados"
            )

        for item in itens_pedido:
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
                    detail="Estoque do produto não encontrado"
                )

            estoque.quantidade = (
                estoque.quantidade + item.quantidade
            )

            db.add(estoque)

        db.flush()

    db.add(novo_pagamento)
    db.flush()

    registro_auditoria = Auditoria(
        id_usuario=dados_token["id_usuario"],
        acao=f"PAGAMENTO_{resultado}",
        entidade="PAGAMENTO",
        id_entidade=novo_pagamento.id_pagamento,
        detalhes=(
            f"Pagamento do pedido {pedido.id_pedido} "
            f"com resultado {resultado}"
        )
    )

    db.add(registro_auditoria)

    db.commit()
    db.refresh(novo_pagamento)

    return novo_pagamento