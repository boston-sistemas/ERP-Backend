from datetime import UTC, datetime, timedelta

from authlib.jose import jwt

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import TokenFailures
from src.security.models import Usuario
from src.security.schemas import AccessTokenData, RefreshTokenData

SECRET_KEY = "your_secret_key"
SIGNING_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION_MINUTES = 15
REFRESH_TOKEN_EXPIRATION_DAYS = 8


class TokenService:
    @staticmethod
    def create_token(payload: dict) -> str:
        header = {"alg": SIGNING_ALGORITHM}
        encoded_jwt = jwt.encode(header, payload, SECRET_KEY).decode("utf-8")

        return encoded_jwt

    @staticmethod
    def create_access_token(user: Usuario, accesos: list[str]) -> tuple[str, datetime]:
        expiration = datetime.now(UTC) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRATION_MINUTES
        )
        payload = {
            "sub": user.usuario_id,
            "username": user.username,
            "accesos": accesos,
            "aud": "authenticated",
            "type": "access",
            "exp": expiration,
        }

        encoded_jwt = TokenService.create_token(payload)
        return encoded_jwt, expiration

    @staticmethod
    def create_refresh_token(user: Usuario, sid: str) -> tuple[str, datetime]:
        expiration = datetime.now(UTC) + timedelta(hours=REFRESH_TOKEN_EXPIRATION_DAYS)
        payload = {
            "sub": user.usuario_id,
            "username": user.username,
            "sid": sid,
            "aud": "authenticated",
            "type": "refresh",
            "exp": expiration,
        }

        encoded_jwt = TokenService.create_token(payload)
        return encoded_jwt, expiration

    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(token, SECRET_KEY)

    @staticmethod
    def verify_token(token: str) -> Result[dict, CustomException]:
        failure = TokenFailures.INVALID_TOKEN_FAILURE
        try:
            decoded_token = jwt.decode(token, SECRET_KEY)
            if decoded_token["exp"] < datetime.now(UTC).timestamp():
                return failure
            return Success(decoded_token)

        except Exception as e:
            print(f"Error al verificar el token: {e}")
            return failure

    @staticmethod
    def verify_refresh_token(
        token: str | None,
    ) -> Result[RefreshTokenData, CustomException]:
        if token is None:
            return TokenFailures.MISSING_REFRESH_TOKEN_FAILURE

        verification_result = TokenService.verify_token(token)
        if verification_result.is_failure:
            return verification_result

        claims: dict = verification_result.value
        if claims.get("type", "") != "refresh":
            return TokenFailures.INVALID_TOKEN_TYPE_FAILURE

        return Success(RefreshTokenData(user_id=claims["sub"], sesion_id=claims["sid"]))

    @staticmethod
    def verify_access_token(
        token: str | None,
    ) -> Result[AccessTokenData, CustomException]:
        if token is None:
            return TokenFailures.MISSING_ACCESS_TOKEN_FAILURE

        verification_result = TokenService.verify_token(token)
        if verification_result.is_failure:
            return verification_result

        claims: dict = verification_result.value
        if claims.get("type", "") != "access":
            return TokenFailures.INVALID_TOKEN_TYPE_FAILURE

        return Success(
            AccessTokenData(user_id=claims["sub"], accesos=claims["accesos"])
        )
