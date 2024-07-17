from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.security.models import UsuarioSesion


class UserSesionRepository(BaseRepository[UsuarioSesion]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(UsuarioSesion, db, flush)

    @staticmethod
    def include_user() -> Load:
        return joinedload(UsuarioSesion.usuario)

    async def find_user_sesion(
        self, filter: BinaryExpression, include_user=False
    ) -> UsuarioSesion | None:
        options: list[Load] = []

        if include_user:
            options.append(self.include_user())

        current_sesion = await self.find(filter, options=options)

        return current_sesion
