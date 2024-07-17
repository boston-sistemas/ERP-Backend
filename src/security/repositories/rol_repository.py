from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.security.models import Rol


class RolRepository(BaseRepository[Rol]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Rol, db, flush)

    @staticmethod
    def include_accesos() -> Load:
        return joinedload(Rol.accesos)

    async def find_rol(
        self, filter: BinaryExpression, include_accesos=False
    ) -> Rol | None:
        options: list[Load] = []

        if include_accesos:
            options.append(self.include_accesos())

        rol = await self.find(filter, options=options)

        return rol
