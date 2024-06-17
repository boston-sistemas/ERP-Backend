from datetime import UTC, datetime, timedelta
from typing import Any

import pytz
from authlib.jose import jwt
from core.config import settings
from passlib.context import CryptContext

from security.models import Sesion, Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
SIGNING_ALGORITHM = settings.SIGNING_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 8


def verify_password(plain_password: str, hashed_password: str) -> bool:
    correct_password: bool = pwd_context.verify(plain_password, hashed_password)
    return correct_password


def get_password_hash(password: str) -> str:
    hashed_password: str = pwd_context.hash(password, rounds=12)
    return hashed_password


def validate_user_status(usuario: Usuario | None) -> bool:
    if not usuario:
        return False

    if not usuario.is_active:
        return False

    if usuario.blocked_until and usuario.blocked_until.astimezone(UTC) > datetime.now(
        UTC
    ):
        return False

    return True


def validate_sesion(sesion: Sesion):
    if sesion.not_after.astimezone(UTC) < datetime.now(UTC):
        return False

    return validate_user_status(sesion.usuario)


def authenticate_user(usuario: Usuario, password: str) -> bool:
    if not verify_password(password, usuario.password):
        return False

    return True


def get_valid_acceses(usuario: Usuario) -> list[str]:
    return ["REVISION_STOCK", "PROGRAMACION_TINTORERIA"]


def create_token(payload: dict) -> str:
    header = {"alg": SIGNING_ALGORITHM}
    encoded_jwt = jwt.encode(header, payload, SECRET_KEY).decode("utf-8")

    return encoded_jwt


def create_access_token(payload: dict[str, Any], iat: datetime | None = None) -> str:
    if not iat:
        iat = datetime.now(UTC)

    expire = iat + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"aud": "authenticated", "iat": iat, "exp": expire})

    encoded_jwt = create_token(payload)
    return encoded_jwt


def create_refresh_token(payload: dict[str, Any], iat: datetime | None = None) -> str:
    if not iat:
        iat = datetime.now(UTC)

    expire = iat + timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    payload.update({"iat": iat, "exp": expire})

    encoded_jwt = create_token(payload)
    return encoded_jwt


def verify_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY)
        if decoded_token["exp"] < datetime.now(UTC).timestamp():
            return None
        return decoded_token

    except Exception as e:
        print(f"Error al verificar el token: {e}")
        return None


def calculate_session_expiration(at: datetime | None) -> datetime:
    if not at:
        at = datetime.now(UTC)
    local_timezone = pytz.timezone("America/Lima")
    session_expiration = at + timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    return session_expiration.astimezone(local_timezone).replace(tzinfo=None)
