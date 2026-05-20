from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from src.routes.auth_routes import auth_router
from src.routes.order_routes import order_router

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

app = FastAPI()

app.include_router(auth_router)
app.include_router(order_router)
