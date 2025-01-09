from datetime import datetime

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    contains_eager,
    joinedload,
)
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.constants import (
    SUPPLY_FAMILY_ID,
    YARN_SUBFAMILY_ID,
)
from src.operations.models import InventoryItem, OrdenCompra, OrdenCompraDetalle


class OrdenCompraRepository(BaseRepository[OrdenCompra]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(OrdenCompra, db, flush)

    @staticmethod
    def include_detalle() -> Load:
        return joinedload(OrdenCompra.detail)

    @staticmethod
    def include_detalle_yarns() -> Load:
        return joinedload(OrdenCompra.detail).joinedload(OrdenCompraDetalle.yarn)

    async def find_yarn_order_by_purchase_order_number(
        self,
        purchase_order_number: str,
        period: int,
        include_detalle: bool = False,
    ) -> OrdenCompra | None:
        options: list[Load] = []
        joins: list[tuple] = []

        joins.append(OrdenCompra.detail)
        joins.append(OrdenCompraDetalle.yarn)

        current_year = period
        start_of_year = datetime(current_year, 1, 1).date()
        end_of_year = datetime(current_year, 12, 31).date()

        filter_conditions = [
            OrdenCompra.company_code == MECSA_COMPANY_CODE,
            OrdenCompra.purchase_order_number == purchase_order_number,
            func.locate("TITULO GRATUITO", OrdenCompra.payment_method) == 0,
            InventoryItem.family_id == SUPPLY_FAMILY_ID,
            InventoryItem.subfamily_id == YARN_SUBFAMILY_ID,
            OrdenCompra.issue_date >= start_of_year,
            OrdenCompra.issue_date <= end_of_year,
            or_(
                OrdenCompra.status_flag == "P",
                OrdenCompra.status_flag == "C",
                OrdenCompra.status_flag == "A",
            ),
        ]

        filter = and_(*filter_conditions)

        if include_detalle:
            options.append(
                contains_eager(OrdenCompra.detail).contains_eager(
                    OrdenCompraDetalle.yarn
                )
            )

        orden = await self.find(filter=filter, joins=joins, options=options)

        return orden

    async def find_ordenes_yarn(
        self,
        period: int,
        include_detalle: bool = False,
    ) -> list[OrdenCompra]:
        options: list[Load] = []
        joins: list[tuple] = []

        joins.append(OrdenCompra.detail)
        joins.append(OrdenCompraDetalle.yarn)

        current_year = period
        start_of_year = datetime(current_year, 1, 1).date()
        end_of_year = datetime(current_year, 12, 31).date()

        filter = and_(
            OrdenCompra.company_code == MECSA_COMPANY_CODE,
            OrdenCompra.status_flag == "P",
            func.locate("TITULO GRATUITO", OrdenCompra.payment_method) == 0,
            InventoryItem.family_id == SUPPLY_FAMILY_ID,
            InventoryItem.subfamily_id == YARN_SUBFAMILY_ID,
            OrdenCompra.issue_date >= start_of_year,
            OrdenCompra.issue_date <= end_of_year,
        )

        if include_detalle:
            options.append(
                contains_eager(OrdenCompra.detail).contains_eager(
                    OrdenCompraDetalle.yarn
                )
            )

        ordenes = await self.find_all(
            filter=filter, joins=joins, options=options, apply_unique=True
        )

        return ordenes
