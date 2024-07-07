from datetime import datetime

from pydantic import BaseModel

from .usuario_rol_acceso_schema import UsuarioSchema


class LoginForm(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    access_token: str
    access_token_expiration: datetime
    refresh_token: str | None = None
    refresh_token_expiration: datetime | None = None
    token_type: str = "bearer"
    usuario: UsuarioSchema


class LogoutResponse(BaseModel):
    message: str = "Sesión cerrada exitosamente"


class RefreshResponse(BaseModel):
    access_token: str
    access_token_expiration: datetime
    token_type: str = "bearer"
