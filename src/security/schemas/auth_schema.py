from datetime import datetime

from pydantic import BaseModel

from .user_rol_acceso_schema import UsuarioSchema


class LoginForm(BaseModel):
    username: str
    password: str


class LoginWithTokenForm(LoginForm):
    token: str


class LoginResponse(BaseModel):
    message: str
    access_token: str
    access_token_expiration_at: datetime
    refresh_token: str | None = None
    refresh_token_expiration_at: datetime | None = None
    token_type: str = "bearer"
    usuario: UsuarioSchema


class LogoutResponse(BaseModel):
    message: str = "Sesión cerrada exitosamente"


class RefreshResponse(BaseModel):
    access_token: str
    access_token_expiration_at: datetime
    token_type: str = "bearer"


class SendTokenResponse(BaseModel):
    token_expiration_minutes: int
    token_expiration_at: datetime
    email_send_to: str
