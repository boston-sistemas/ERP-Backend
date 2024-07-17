from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import UserSesionFailures
from src.security.models import Usuario, UsuarioSesion
from src.security.repositories import UserRepository, UserSesionRepository

SESSION_EXPIRATION_HOURS = 8


class UserSesionService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = UserSesionRepository(db)
        self.user_repository = UserRepository(db)

    @staticmethod
    def calculate_expiration() -> datetime:
        # TODO: Analizar si tener en cuenta la zona horaria local
        # local_timezone = pytz.timezone("America/Lima")
        # return expiration.astimezone(local_timezone).replace(tzinfo=None)
        expiration = datetime.now() + timedelta(hours=SESSION_EXPIRATION_HOURS)
        return expiration

    async def read_sesion(
        self, sesion_id: str, include_user: bool = False
    ) -> Result[UsuarioSesion, CustomException]:
        current_sesion = await self.repository.find_user_sesion(
            UsuarioSesion.sesion_id == UUID(sesion_id), include_user=include_user
        )
        if current_sesion is not None:
            return Success(current_sesion)

        return UserSesionFailures.SESION_NOT_FOUND_FAILURE

    async def read_sesiones(self) -> list[UsuarioSesion]:
        return await self.repository.find_all(
            options=(self.repository.include_user(),), apply_unique=True
        )

    async def create_sesion(self, user: Usuario, ip: str) -> UUID:
        user_sesion = UsuarioSesion(
            sesion_id=uuid4(),
            usuario_id=user.usuario_id,
            not_after=self.calculate_expiration(),
            ip=ip,
        )

        # user.last_login = datetime.now()
        # await self.user_repository.save(user)
        await self.repository.save(user_sesion)
        return user_sesion.sesion_id

    @staticmethod
    def validate_sesion_instance(
        current_sesion: UsuarioSesion,
    ) -> Result[UsuarioSesion, CustomException]:
        if current_sesion.not_after.astimezone(UTC) < datetime.now(UTC):
            return UserSesionFailures.SESION_EXPIRED_FAILURE

        return Success(UsuarioSesion)

    async def close_sesion(self, sesion_id: str) -> Result[None, CustomException]:
        result = await self.read_sesion(sesion_id)
        if result.is_failure:
            return result

        current_sesion: UsuarioSesion = result.value

        validation_result = self.validate_sesion_instance(current_sesion)
        if validation_result.is_failure:
            return validation_result

        current_sesion.not_after = datetime.now()
        await self.repository.save(current_sesion)
        return Success(None)
