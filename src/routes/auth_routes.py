from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.models.models import Usuario
from src.schemas.schemas import LoginSchema, UsuarioSchema
from src.utils.dependecies import get_db, verificar_token
from src.utils.utils import autenticar_usuario, bcrypt_context, criar_token

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/")
async def autenticar():
    return {"mensagem": "Voce acessou as rotas de autenticacao."}


@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Annotated[Session, Depends(get_db)]):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()

    if usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario ja cadastrado com este e-mail.",
        )

    senha_cryptografada = bcrypt_context.hash(usuario_schema.senha)

    novo_usuario = Usuario(
        nome=usuario_schema.nome,
        email=usuario_schema.email,
        senha=senha_cryptografada,
        ativo=usuario_schema.ativo,
        admin=usuario_schema.admin,
    )
    session.add(novo_usuario)
    session.commit()

    return {"mensagem": "Usuario cadastrado com sucesso"}


@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Annotated[Session, Depends(get_db)]):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario nao encontrado")

    access_token = criar_token(usuario.id)
    refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}


@auth_router.post("/login-form")
async def login_form(
    dados_formulario: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_db)],
):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario nao encontrado")

    access_token = criar_token(usuario.id)
    return {"access_token": access_token, "token_type": "Bearer"}


@auth_router.get("/refresh")
async def use_refresh_token(usuario: Annotated[Usuario, Depends(verificar_token)]):
    access_token = criar_token(usuario.id)
    return {"access_token": access_token, "token_type": "Bearer"}
