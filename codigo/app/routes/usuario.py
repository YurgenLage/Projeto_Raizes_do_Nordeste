from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from codigo.app.database import SessionLocal
from codigo.app.models.usuario import Usuario
from codigo.app.schemas.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    LoginRequest
)
from codigo.app.auth import (
    criar_token,
    decodificar_token,
    verificar_perfil
)


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=UsuarioResponse, status_code=201)
def criar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    usuario_existente = (
        db.query(Usuario)
        .filter(Usuario.email == usuario.email)
        .first()
    )

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    # Cadastro público só pode criar cliente
    if usuario.perfil != "CLIENTE":
        raise HTTPException(
            status_code=403,
            detail="Cadastro público permite apenas perfil CLIENTE"
        )

    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=pwd_context.hash(usuario.senha),
        perfil="CLIENTE",
        consentimento_dados=usuario.consentimento_dados
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


@router.post("/login")
def login(
    dados: LoginRequest,
    db: Session = Depends(get_db)
):
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == dados.email)
        .first()
    )

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )

    senha_correta = pwd_context.verify(
        dados.senha,
        usuario.senha_hash
    )

    if not senha_correta:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=403,
            detail="Usuário inativo"
        )

    token = criar_token({
        "sub": str(usuario.id_usuario),
        "perfil": usuario.perfil
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    verificar_perfil(
        dados_token,
        ["GERENTE", "ADMIN"]
    )

    usuarios = db.query(Usuario).all()

    return usuarios


@router.get("/me", response_model=UsuarioResponse)
def usuario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.id_usuario == dados_token["id_usuario"]
        )
        .first()
    )

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return usuario


@router.get("/area-administrativa")
def area_administrativa(
    credenciais: HTTPAuthorizationCredentials = Depends(security)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    verificar_perfil(
        dados_token,
        ["GERENTE", "ADMIN"]
    )

    return {
        "mensagem": "Acesso autorizado à área administrativa"
    }


@router.get("/{id_usuario}", response_model=UsuarioResponse)
def buscar_usuario(
    id_usuario: int,
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    dados_token = decodificar_token(token)

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id_usuario == id_usuario)
        .first()
    )

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    if (
        dados_token["perfil"] not in ["GERENTE", "ADMIN"]
        and dados_token["id_usuario"] != id_usuario
    ):
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para visualizar este usuário"
        )

    return usuario