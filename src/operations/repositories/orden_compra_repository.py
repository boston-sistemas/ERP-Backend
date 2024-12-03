from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import BinaryExpression, and_, func
from sqlalchemy.orm import (
    joinedload,
    aliased,
    contains_eager,
)
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.operations.models import OrdenCompra, OrdenCompraDetalle, Yarn


class OrdenCompraRepository(BaseRepository[OrdenCompra]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(OrdenCompra, db, flush)

    @staticmethod
    def include_detalle() -> Load:
        return joinedload(OrdenCompra.detalle)

    @staticmethod
    def include_detalle_yarns() -> Load:
        return joinedload(OrdenCompra.detalle).joinedload(OrdenCompraDetalle.yarn)

    async def find_ordenes_yarn(
        self,
        include_detalle: bool = False,
    ) -> list[OrdenCompra]:
        options: list[Load] = []
        joins: list[tuple] = []

        joins.append(OrdenCompra.detalle)
        joins.append(OrdenCompraDetalle.yarn)

        filter = and_(
            OrdenCompra.codcia == '001',
            OrdenCompra.status_flag == 'P',
            func.locate('TITULO GRATUITO', OrdenCompra.payment_method) == 0,
            Yarn.family_code == '03',
            Yarn.subfamily_code == '09'
        )

        options.append(
            contains_eager(OrdenCompra.detalle).contains_eager(OrdenCompraDetalle.yarn)
        )

        ordenes = await self.find_all(
            filter=filter, joins=joins, options=options, apply_unique=True
        )

        return ordenes



