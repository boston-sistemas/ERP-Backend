from authlib.jose import jwt
from datetime import UTC, datetime, timedelta
from passlib.context import CryptContext
import pytz
from typing import Any

from config.settings import settings
from mecsa_erp.usuarios.models import Usuario

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


def authenticate_user(db_usuario: Usuario, password: str) -> bool:
    if not db_usuario:
        return False

    if not db_usuario.is_active:
        return False

    if db_usuario.blocked_until and db_usuario.blocked_until.astimezone(
        UTC
    ) > datetime.now(UTC):
        return False

    if not verify_password(password, db_usuario.password):
        return False

    return True


def get_valid_acceses(usuario: Usuario) -> list[str]:
    return ["REVISION_STOCK", "PROGRAMACION_TINTORERIA"]


def create_token(payload: dict) -> str:
    header = {"alg": SIGNING_ALGORITHM}
    encoded_jwt = jwt.encode(header, payload, SECRET_KEY).decode("utf-8")

    return encoded_jwt


def create_access_token(payload: dict[str, Any], iat: datetime | None) -> str:
    if not iat:
        iat = datetime.now(UTC)

    expire = iat + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"aud": "authenticated", "iat": iat, "exp": expire})

    encoded_jwt = create_token(payload)
    return encoded_jwt


def create_refresh_token(payload: dict[str, Any], iat: datetime | None) -> str:
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
