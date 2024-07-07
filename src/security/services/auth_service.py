from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException, UnauthorizedException
from src.core.result import Failure, Result, Success
from src.security.models import Usuario
from src.security.schemas import (
    LoginForm,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    RefreshTokenData,
)

from .rol_service import RolService
from .token_service import TokenService
from .user_service import UserService
from .user_sesion_service import UserSesionService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)
        self.user_sesion_service = UserSesionService(db)
        self.token_service = TokenService
        self.rol_service = RolService(db)

    @staticmethod
    def validate_user_status(user: Usuario) -> bool:
        if not user.is_active:
            return False

        if user.blocked_until and user.blocked_until.astimezone(UTC) > datetime.now(
            UTC
        ):
            return False

        return True

    async def get_valid_user_access(self, user: Usuario) -> list[str]:
        return ["REVISION_STOCK", "PROGRAMACION_TINTORERIA"]

    async def login(
        self, form: LoginForm, ip: str
    ) -> Result[LoginResponse, CustomException]:
        error = UnauthorizedException("Credenciales no válidas.")

        user_result = await self.user_service.read_user_by_username(
            form.username, include_roles=True
        )
        if user_result.is_failure:
            return Failure(error)

        user: Usuario = user_result.value
        if not self.validate_user_status(user):
            return Failure(error)

        if not self.user_service.verify_password(form.password, user.password):
            return Failure(error)

        id: UUID = await self.user_sesion_service.create_sesion(user, ip)
        message = "Inicio de sesión exitoso."

        access_token, access_token_expiration = self.token_service.create_access_token(
            user=user,
            accesos=(await self.get_valid_user_access(user)),
        )
        # refresh_token None if user.reset_password else self.token_service.create_refresh_token()
        # message = "Es necesario cambiar contraseña"
        refresh_token, refresh_token_expiration = (
            self.token_service.create_refresh_token(user=user, sid=str(id))
        )

        return Success(
            LoginResponse(
                message=message,
                access_token=access_token,
                access_token_expiration=access_token_expiration,
                refresh_token=refresh_token,
                refresh_token_expiration=refresh_token_expiration,
                usuario=user,
            )
        )

    async def refresh_access_token(
        self, refresh_token: str | None
    ) -> Result[RefreshResponse, CustomException]:
        verification_result = self.token_service.verify_refresh_token(refresh_token)
        if verification_result.is_failure:
            return verification_result

        token_data: RefreshTokenData = verification_result.value
        sesion_result = await self.user_sesion_service.read_sesion(token_data.sesion_id)
        if sesion_result.is_failure:
            return sesion_result

        validation_result = self.user_sesion_service.validate_sesion_instance(
            current_sesion=sesion_result.value
        )
        if validation_result.is_failure:
            return validation_result

        user_result = await self.user_service.read_user(
            token_data.user_id, include_roles=True
        )
        if user_result.is_failure:
            return user_result

        user: Usuario = user_result.value
        access_token, access_token_expiration = self.token_service.create_access_token(
            user=user,
            accesos=(await self.get_valid_user_access(user)),
        )

        return Success(
            RefreshResponse(
                access_token=access_token,
                access_token_expiration=access_token_expiration,
            )
        )

    async def logout(
        self, refresh_token: str | None
    ) -> Result[LogoutResponse, CustomException]:
        verification_result = self.token_service.verify_refresh_token(refresh_token)
        if verification_result.is_failure:
            return verification_result

        token_data: RefreshTokenData = verification_result.value
        closure_result = await self.user_sesion_service.close_sesion(
            token_data.sesion_id
        )

        if closure_result.is_failure:
            return closure_result

        return Success(LogoutResponse())
