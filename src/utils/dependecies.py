from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session, sessionmaker

from src.models.models import Usuario, db
from src.utils.utils import ALGORITHM, SECRET_KEY

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db)
    session = Session()
    try:
        yield session
    finally:
        session.close()

async def verificar_token(token: Annotated[str, Depends(oauth2_schema)], session: Annotated[Session, Depends(get_db)]):
    try:
        dic_info = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = int(dic_info.get("sub"))
    except (JWTError, ValueError) as erro:
        print(erro)
        raise (HTTPException(status_code=401, detail="ACESSO NEGADO!!!")) from None

    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Invalido")
    return usuario
