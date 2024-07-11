from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.operations.models import OrdenServicioTejeduria


class OrdenServicioTejeduriaRepository(BaseRepository[OrdenServicioTejeduria]):
    def __init__(self, db: AsyncSession, commit: bool = True) -> None:
        super().__init__(OrdenServicioTejeduria, db, commit)

    @staticmethod
    def include_detalle() -> Load:
        return joinedload(OrdenServicioTejeduria.detalles)

    @staticmethod
    def include_proveedor() -> Load:
        return joinedload(OrdenServicioTejeduria.proveedor)

    async def find_orden(
        self,
        filter: BinaryExpression,
        include_detalle: bool = False,
        include_proveedor: bool = False,
    ) -> OrdenServicioTejeduria | None:
        options: list[Load] = []

        if include_detalle:
            options.append(self.include_detalle())

        if include_proveedor:
            options.append(self.include_proveedor())

        orden = await self.find(filter, options=options)

        return orden

    async def find_ordenes(
        self,
        filter: BinaryExpression = None,
        include_detalle: bool = False,
        include_proveedor: bool = False,
    ) -> list[OrdenServicioTejeduria]:
        options: list[Load] = []

        if include_detalle:
            options.append(self.include_detalle())

        if include_proveedor:
            options.append(self.include_proveedor())

        ordenes = await self.find_all(
            filter=filter, options=options, apply_unique=True if options else False
        )

        return ordenes
