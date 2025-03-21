from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import AuthFailures
from src.security.models import Acceso, Usuario
from src.security.repositories import ModuloSistemaRepository
from src.security.schemas import (
    AccessesWithOperationsListSchema,
    LoginForm,
    LoginResponse,
    LoginWithTokenForm,
    LogoutResponse,
    RefreshResponse,
    RefreshTokenData,
    RolSchema,
    SendTokenResponse,
)

from ...core.services.email_service import EmailService
from .acceso_service import AccesoService
from .rol_service import RolService
from .token_service import TokenService
from .user_service import UserService
from .user_sesion_service import UserSesionService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)
        self.user_sesion_service = UserSesionService(db)
        self.token_service = TokenService(db)
        self.rol_service = RolService(db)
        self.modulo_repository = ModuloSistemaRepository(db)
        self.email_service = EmailService()
        self.acceso_service = AccesoService(db)

    @staticmethod
    def validate_user_status(user: Usuario) -> bool:
        if not user.is_active:
            return False

        if user.blocked_until and user.blocked_until.astimezone(UTC) > datetime.now(
            UTC
        ):
            return False

        return True

    async def is_valid_access_operation_to_user(
        self,
        user_id: int,
        access_id: int,
        operation_id: int,
    ) -> bool:
        user_result = await self.user_service.read_user(user_id, include_roles=True)
        if user_result.is_failure:
            return False

        user: Usuario = user_result.value
        if not self.validate_user_status(user):
            return False

        for rol in user.roles:
            if rol.is_active:
                validation_result = await self.acceso_service._read_access(
                    access_id=access_id
                )

                if validation_result.is_failure:
                    return False

                access: Acceso = validation_result.value

                if access.is_active:
                    validation_result = await self.rol_service.has_access_operation(
                        rol_id=rol.rol_id,
                        acceso_id=access_id,
                        operation_id=operation_id,
                    )

                    if validation_result.is_success:
                        return True

        return False

    async def get_valid_user_access(self, user: Usuario) -> list[Acceso]:
        rol_ids = [rol.rol_id for rol in user.roles if rol.is_active]
        accesos: list[Acceso] = []
        for rol_id in rol_ids:
            rol_result = await self.rol_service.read_rol(
                rol_id=rol_id, include_access_operation=True
            )
            rol = rol_result.value
            accesos.extend([access for access in rol.access if access.is_active])
        return accesos

    async def _validate_user_credentials(
        self, username: str, password: str
    ) -> Result[Usuario, CustomException]:
        user_result = await self.user_service.read_user_by_username(
            username, include_roles=True
        )
        if user_result.is_failure:
            return AuthFailures.INVALID_CREDENTIALS_FAILURE

        user: Usuario = user_result.value
        if not self.validate_user_status(user):
            return AuthFailures.INVALID_CREDENTIALS_FAILURE

        if not self.user_service.verify_password(password, user.password):
            return AuthFailures.INVALID_CREDENTIALS_FAILURE

        return Success(user)

    async def login(
        self, form: LoginWithTokenForm, ip: str
    ) -> Result[LoginResponse, CustomException]:
        validation_result = await self._validate_user_credentials(
            form.username, form.password
        )
        if validation_result.is_failure:
            return validation_result

        user: Usuario = validation_result.value
        # token_verification_result = await self.token_service.verify_auth_token(
        #     user.usuario_id, form.token
        # )
        #
        # if token_verification_result.is_failure:
        #     return token_verification_result

        id: UUID = await self.user_sesion_service.create_sesion(user, ip)
        message = "Inicio de sesión exitoso."

        await self.modulo_repository.expunge_all_objects(user.roles)

        access_token, access_token_expiration_at = (
            self.token_service.create_access_token(
                user=user,
            )
        )
        refresh_token, refresh_token_expiration_at = (
            self.token_service.create_refresh_token(user=user, sid=str(id))
        )

        return Success(
            LoginResponse(
                message=message,
                access_token=access_token,
                access_token_expiration_at=access_token_expiration_at,
                refresh_token=refresh_token,
                refresh_token_expiration_at=refresh_token_expiration_at,
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
        access_token, access_token_expiration_at = (
            self.token_service.create_access_token(
                user=user,
                accesos=(await self.get_valid_user_access(user)),
                modules=(await self.modulo_repository.find_all()),
            )
        )

        return Success(
            RefreshResponse(
                access_token=access_token,
                access_token_expiration_at=access_token_expiration_at,
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

    async def send_auth_token(self, form: LoginForm) -> Result[SendTokenResponse, None]:
        validation_result = await self._validate_user_credentials(
            form.username, form.password
        )
        if validation_result.is_failure:
            return validation_result

        user: Usuario = validation_result.value
        await self.token_service.delete_auth_tokens(user.usuario_id)
        auth_token, expiration_at = await self.token_service.create_auth_token(
            user.usuario_id
        )
        await self.email_service.send_auth_token_email(
            user.email,
            user.display_name,
            auth_token,
            self.token_service.AUTH_TOKEN_EXPIRATION_MINUTES,
        )
        return Success(
            SendTokenResponse(
                token_expiration_at=expiration_at,
                token_expiration_minutes=self.token_service.AUTH_TOKEN_EXPIRATION_MINUTES,
                email_send_to=user.email,
            )
        )

    async def read_accesses_operations(
        self, access_token: str | None
    ) -> Result[AccessesWithOperationsListSchema, CustomException]:
        verification_result = self.token_service.verify_access_token(token=access_token)
        if verification_result.is_failure:
            return verification_result

        token_data = self.token_service.decode_token(access_token)

        user_result = await self.user_service.read_user(
            user_id=token_data.sub, include_roles=True
        )
        if user_result.is_failure:
            return user_result

        user: Usuario = user_result.value
        await self.modulo_repository.expunge_all_objects(user.roles)

        roles: list[RolSchema] = []
        for rol in user.roles:
            rol_result = await self.rol_service.read_rol(
                rol_id=rol.rol_id, include_access_operation=True
            )
            if rol_result.is_failure:
                return rol_result

            roles.append(rol_result.value)

        return Success(
            AccessesWithOperationsListSchema(
                roles=roles,
            )
        )
