from datetime import UTC, datetime, timedelta

from authlib.jose import jwt

from src.core.exceptions import CustomException, UnauthorizedException
from src.core.result import Failure, Result, Success
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
        error = UnauthorizedException("Token inválido.")
        try:
            decoded_token = jwt.decode(token, SECRET_KEY)
            if decoded_token["exp"] < datetime.now(UTC).timestamp():
                return Failure(error)
            return Success(decoded_token)

        except Exception as e:
            print(f"Error al verificar el token: {e}")
            return Failure(error)

    @staticmethod
    def verify_refresh_token(
        token: str | None,
    ) -> Result[RefreshTokenData, CustomException]:
        if token is None:
            return Failure(UnauthorizedException("Refresh token missing."))

        verification_result = TokenService.verify_token(token)
        if verification_result.is_failure:
            return verification_result

        claims: dict = verification_result.value
        if claims.get("type", "") != "refresh":
            return Failure(UnauthorizedException("Token invalido"))

        return Success(RefreshTokenData(user_id=claims["sub"], sesion_id=claims["sid"]))

    @staticmethod
    def verify_access_token(
        token: str | None,
    ) -> Result[AccessTokenData, CustomException]:
        if token is None:
            return Failure(UnauthorizedException("Access token missing."))

        verification_result = TokenService.verify_token(token)
        if verification_result.is_failure:
            return verification_result

        claims: dict = verification_result.value
        if claims.get("type", "") != "access":
            return Failure(UnauthorizedException("Token inválido."))

        return Success(
            AccessTokenData(user_id=claims["sub"], accesos=claims["accesos"])
        )

    @staticmethod
    def is_access_token(token: str) -> bool:
        payload = TokenService.decode_token(token)
        return payload.get("type", "") == "access"

    @staticmethod
    def is_refresh_token(token: str) -> bool:
        payload = TokenService.decode_token(token)
        return payload.get("type", "") == "refresh"
