from authlib.jose import jwt
from datetime import UTC, datetime, timedelta
from passlib.context import CryptContext

from config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
SIGNING_ALGORITHM = settings.SIGNING_ALGORITHM


def verify_password(plain_password: str, hashed_password: str) -> bool:
    correct_password: bool = pwd_context.verify(plain_password, hashed_password)
    return correct_password


def get_password_hash(password: str) -> str:
    hashed_password: str = pwd_context.hash(password, rounds=12)
    return hashed_password


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    header = {"alg": SIGNING_ALGORITHM}
    payload = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=10)

    payload.update({"exp": expire})

    encoded_jwt = jwt.encode(header, payload, SECRET_KEY).decode("utf-8")

    return encoded_jwt


def verify_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY)
        if decoded_token["exp"] < datetime.now(UTC).timestamp():
            return None
        return decoded_token

    except Exception as e:
        print(f"Error al verificar el token: {e}")
        return None
