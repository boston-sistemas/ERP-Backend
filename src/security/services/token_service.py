import secrets
import string
from datetime import UTC, datetime, timedelta

from authlib.jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import TokenFailures
from src.security.models import Acceso, AuthToken, ModuloSistema, Usuario
from src.security.repositories import AuthTokenRepository
from src.security.schemas import AccessTokenData, RefreshTokenData

from .hash_service import HashService

SECRET_KEY = settings.SECRET_KEY
SIGNING_ALGORITHM = settings.SIGNING_ALGORITHM
ACCESS_TOKEN_EXPIRATION_MINUTES = 15
REFRESH_TOKEN_EXPIRATION_HOURS = 8
AUTH_TOKEN_LENGTH = 6


class TokenService:
    AUTH_TOKEN_EXPIRATION_MINUTES = 5

    def __init__(self, db: AsyncSession):
        self.repository = AuthTokenRepository(db)

    @staticmethod
    def create_token(payload: dict) -> str:
        header = {"alg": SIGNING_ALGORITHM}
        encoded_jwt = jwt.encode(header, payload, SECRET_KEY).decode("utf-8")

        return encoded_jwt

    @staticmethod
    def create_access_token(user: Usuario) -> tuple[str, datetime]:
        expiration_at = datetime.now(UTC) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRATION_MINUTES
        )
        payload = {
            "sub": user.usuario_id,
            "username": user.username,
            "aud": "authenticated",
            "type": "access",
            "exp": expiration_at,
        }

        encoded_jwt = TokenService.create_token(payload)
        return encoded_jwt, expiration_at

    @staticmethod
    def create_refresh_token(user: Usuario, sid: str) -> tuple[str, datetime]:
        expiration_at = datetime.now(UTC) + timedelta(
            hours=REFRESH_TOKEN_EXPIRATION_HOURS
        )
        payload = {
            "sub": user.usuario_id,
            "username": user.username,
            "sid": sid,
            "aud": "authenticated",
            "type": "refresh",
            "exp": expiration_at,
        }

        encoded_jwt = TokenService.create_token(payload)
        return encoded_jwt, expiration_at

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

        return Success(AccessTokenData(user_id=claims["sub"]))

    @staticmethod
    def _generate_auth_token(length=6):
        alphabet = string.digits + string.ascii_letters
        token = "".join(secrets.choice(alphabet) for _ in range(length))
        return token

    async def create_auth_token(self, user_id: int) -> tuple[str, datetime]:
        expiration_time = datetime.now() + timedelta(
            minutes=self.AUTH_TOKEN_EXPIRATION_MINUTES
        )
        auth_token = self._generate_auth_token(length=AUTH_TOKEN_LENGTH)
        hashed_auth_token = HashService.hash_text(auth_token)
        instance = AuthToken(
            codigo=hashed_auth_token, usuario_id=user_id, expiration_at=expiration_time
        )
        await self.repository.save(instance)
        return auth_token, expiration_time

    async def verify_auth_token(
        self, user_id: int, codigo: str
    ) -> Result[AuthToken, CustomException]:
        auth_token = await self.repository.find(filter=AuthToken.usuario_id == user_id)
        if (
            auth_token is None
            or (not HashService.verify_text(codigo, auth_token.codigo))
            or auth_token.expiration_at < datetime.now()
        ):
            return TokenFailures.INVALID_TOKEN_FAILURE
        await self.repository.delete(auth_token)
        return Success(auth_token)

    async def delete_auth_tokens(self, user_id: int):
        filter_expression = AuthToken.usuario_id == user_id
        auth_tokens = await self.repository.find_all(filter=filter_expression)
        await self.repository.delete_all(auth_tokens)
