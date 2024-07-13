from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import AuthFailures
from src.security.models import Acceso, Usuario
from src.security.repositories import ModuloSistemaRepository
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
        self.modulo_repository = ModuloSistemaRepository(db)

    @staticmethod
    def validate_user_status(user: Usuario) -> bool:
        if not user.is_active:
            return False

        if user.blocked_until and user.blocked_until.astimezone(UTC) > datetime.now(
            UTC
        ):
            return False

        return True

    async def get_valid_user_access(self, user: Usuario) -> list[Acceso]:
        rol_ids = [rol.rol_id for rol in user.roles if rol.is_active]
        accesos: list[Acceso] = []
        for rol_id in rol_ids:
            rol_result = await self.rol_service.read_rol(rol_id, include_accesos=True)
            rol = rol_result.value
            accesos.extend([acceso for acceso in rol.accesos if acceso.is_active])
        return accesos

    async def login(
        self, form: LoginForm, ip: str
    ) -> Result[LoginResponse, CustomException]:
        failure = AuthFailures.INVALID_CREDENTIALS_FAILURE

        user_result = await self.user_service.read_user_by_username(
            form.username, include_roles=True
        )
        if user_result.is_failure:
            return failure

        user: Usuario = user_result.value
        if not self.validate_user_status(user):
            return failure

        if not self.user_service.verify_password(form.password, user.password):
            return failure

        id: UUID = await self.user_sesion_service.create_sesion(user, ip)
        message = "Inicio de sesión exitoso."

        access_token, access_token_expiration = self.token_service.create_access_token(
            user=user,
            accesos=(await self.get_valid_user_access(user)),
            modules=(await self.modulo_repository.find_all()),
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
            modules=(await self.modulo_repository.find_all()),
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
