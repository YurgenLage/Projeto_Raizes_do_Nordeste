from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from codigo.app.database import Base, engine

from codigo.app.models.usuario import Usuario
from codigo.app.models.unidade import Unidade
from codigo.app.models.produto import Produto
from codigo.app.models.estoque import Estoque
from codigo.app.models.pedido import Pedido
from codigo.app.models.item_pedido import ItemPedido
from codigo.app.models.pagamento import Pagamento
from codigo.app.models.auditoria import Auditoria
from codigo.app.models.fidelidade import Fidelidade
from codigo.app.models.promocao import Promocao

from codigo.app.routes.usuario import router as usuario_router
from codigo.app.routes.unidade import router as unidade_router
from codigo.app.routes.produto import router as produto_router
from codigo.app.routes.estoque import router as estoque_router
from codigo.app.routes.pedido import router as pedido_router
from codigo.app.routes.pagamento import router as pagamento_router
from codigo.app.routes.auditoria import router as auditoria_router
from codigo.app.routes.fidelidade import router as fidelidade_router
from codigo.app.routes.promocao import router as promocao_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="API Raízes do Nordeste",
    version="1.0.0"
)


@app.exception_handler(HTTPException)
async def tratar_erro_http(
    request: Request,
    exc: HTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "ERRO_HTTP",
            "message": str(exc.detail),
            "details": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(
    request: Request,
    exc: RequestValidationError
):
    detalhes = []

    for erro in exc.errors():
        campo = ".".join(
            str(parte) for parte in erro["loc"]
        )

        detalhes.append({
            "field": campo,
            "issue": erro["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "ERRO_VALIDACAO",
            "message": "Os dados enviados são inválidos.",
            "details": detalhes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": request.url.path
        }
    )


app.include_router(usuario_router)
app.include_router(unidade_router)
app.include_router(produto_router)
app.include_router(estoque_router)
app.include_router(pedido_router)
app.include_router(pagamento_router)
app.include_router(auditoria_router)
app.include_router(fidelidade_router)
app.include_router(promocao_router)


@app.get("/")
def inicio():
    return {
        "mensagem": "API Raízes do Nordeste funcionando"
    }