from sqlalchemy import BinaryExpression, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.security.models import Rol, RolAccesoOperation


class RolRepository(BaseRepository[Rol]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Rol, db, flush)

    @staticmethod
    def include_accesses_operations() -> Load:
        return [
            joinedload(Rol.access_operation),
            joinedload(Rol.access_operation).joinedload(RolAccesoOperation.acceso),
            joinedload(Rol.access_operation).joinedload(RolAccesoOperation.operation),
        ]

    async def find_rol_by_id(
        self,
        rol_id: int,
        filter: BinaryExpression = None,
        joins: list[tuple] = None,
        options: list[Load] = None,
        include_access_operation: bool = False,
    ) -> Rol | None:
        options: list[Load] = [] if options is None else options
        base_filter: list[BinaryExpression] = []

        base_filter.append(Rol.rol_id == rol_id)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        if include_access_operation:
            options.extend(self.include_accesses_operations())

        return await self.find(
            filter=filter,
            joins=joins,
            options=options,
        )

    async def find_roles(
        self,
        filter: BinaryExpression = None,
        options: list[Load] = None,
        include_access_operation: bool = False,
        include_inactive: bool = True,
        limit: int = None,
        offset: int = None,
        apply_unique: bool = False,
        joins: list[tuple] = None,
    ) -> list[Rol]:
        options: list[Load] = [] if options is None else options
        base_filter: list[BinaryExpression] = []

        if not include_inactive:
            base_filter.append(Rol.is_active == True)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        if include_access_operation:
            options.extend(self.include_accesses_operations())

        return await self.find_all(
            filter=filter,
            options=options,
            apply_unique=apply_unique,
            joins=joins,
            limit=limit,
            offset=offset,
        )
