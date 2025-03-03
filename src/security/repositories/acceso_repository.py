from sqlalchemy import BinaryExpression, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.security.models import Acceso


class AccesoRepository(BaseRepository[Acceso]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Acceso, db, flush)

    def get_load_options(
        self,
        include_operations: bool = False,
        include_access_operations: bool = False,
        include_rol_accesses_operations: bool = False,
    ) -> list[Load]:
        options: list[Load] = []

        if include_operations:
            options.append(joinedload(Acceso.operations))

        if include_access_operations:
            options.append(joinedload(Acceso.access_operations))

        if include_rol_accesses_operations:
            options.append(joinedload(Acceso.rol_accesses_operations))

        return options

    async def find_access(
        self,
        access_id: int,
        include_operations: bool = False,
        include_access_operations: bool = False,
        include_rol_accesses_operations: bool = False,
        filter: BinaryExpression = None,
        options: list[Load] = None,
    ) -> Acceso:
        options: list[Load] = [] if options is None else options
        base_filter: list[BinaryExpression] = [Acceso.acceso_id == access_id]

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        options.extend(
            self.get_load_options(
                include_operations=include_operations,
                include_access_operations=include_access_operations,
                include_rol_accesses_operations=include_rol_accesses_operations,
            )
        )

        return await self.find(
            filter=filter,
            options=options,
        )

    async def find_accessess(
        self,
        name: str = None,
        filter: BinaryExpression = None,
        options: list[Load] = None,
        joins: list[tuple] = None,
    ) -> list[Acceso]:
        options: list[Load] = [] if options is None else options
        base_filter: list[BinaryExpression] = []

        if name:
            base_filter.append(Acceso.nombre == name)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        return await self.find_all(
            filter=filter,
            options=options,
            joins=joins,
        )
