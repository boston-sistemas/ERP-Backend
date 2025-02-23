from sqlalchemy import BinaryExpression, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.security.models import ModuloSistema


class ModuloSistemaRepository(BaseRepository[ModuloSistema]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(ModuloSistema, db, flush)

    async def find_system_modules(
        self,
        filter: BinaryExpression = None,
        options: list[Load] = None,
        include_inactive: bool = True,
        limit: int = None,
        offset: int = None,
        apply_unique: bool = False,
        joins: list[tuple] = None,
    ) -> list[ModuloSistema]:
        options: list[Load] = [] if options is None else options
        base_filter: list[BinaryExpression] = []

        if not include_inactive:
            base_filter.append(ModuloSistema.is_active == True)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        return await self.find_all(
            filter=filter,
            options=options,
            apply_unique=apply_unique,
            joins=joins,
            limit=limit,
            offset=offset,
        )

    async def find_system_module_by_id(
        self,
        id: str,
        filter: BinaryExpression = None,
        options: list[Load] = None,
        joins: list[tuple] = None,
    ) -> ModuloSistema | None:
        options: list[Load] = [] if options is None else options
        base_filter: list[BinaryExpression] = []

        base_filter.append(ModuloSistema.id == id)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        return await self.find(
            filter=filter,
            options=options,
            joins=joins,
        )
