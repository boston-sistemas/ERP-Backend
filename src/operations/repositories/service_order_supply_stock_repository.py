from typing import Sequence

from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import ServiceOrderSupplyDetail


class ServiceOrderSupplyDetailRepository(BaseRepository[ServiceOrderSupplyDetail]):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(ServiceOrderSupplyDetail, promec_db, flush)

    async def find_service_order_supply_stock_by_product_code_and_storage_code_and_reference_number_and_item_number(
        self,
        product_code: str,
        storage_code: str,
        reference_number: str,
        item_number: int,
        period: int,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        **kwargs,
    ) -> ServiceOrderSupplyDetail | None:
        base_filter = (
            (ServiceOrderSupplyDetail.company_code == MECSA_COMPANY_CODE)
            & (ServiceOrderSupplyDetail.product_code == product_code)
            & (ServiceOrderSupplyDetail.storage_code == storage_code)
            & (ServiceOrderSupplyDetail.reference_number == reference_number)
            & (ServiceOrderSupplyDetail.period == period)
            & (ServiceOrderSupplyDetail.item_number == item_number)
        )
        filter = base_filter & filter if filter is not None else base_filter

        return await self.find(filter=filter, options=options, **kwargs)

    async def find_service_order_supply_stocks_by_service_order_id_and_storage_code(
        self,
        storage_code: str,
        service_order_id: str,
        period: int,
    ) -> list[ServiceOrderSupplyDetail]:
        base_filter = (
            (ServiceOrderSupplyDetail.company_code == MECSA_COMPANY_CODE)
            & (ServiceOrderSupplyDetail.reference_number == service_order_id)
            & (ServiceOrderSupplyDetail.period == period)
            & (ServiceOrderSupplyDetail.storage_code == storage_code)
        )

        filter = base_filter

        return await self.find_all(
            filter=filter,
            order_by=ServiceOrderSupplyDetail.item_number.asc(),
        )

    async def find_service_orders_supply_stock(
        self,
        storage_code: str = None,
        service_order_id: str = None,
        supply_id: str = None,
        period: int = None,
        limit: int = None,
        order_by: Sequence = None,
    ) -> list[ServiceOrderSupplyDetail]:
        base_filter = ServiceOrderSupplyDetail.company_code == MECSA_COMPANY_CODE

        if storage_code:
            base_filter &= ServiceOrderSupplyDetail.storage_code == storage_code

        if service_order_id:
            base_filter &= ServiceOrderSupplyDetail.reference_number == service_order_id

        if supply_id:
            base_filter &= ServiceOrderSupplyDetail.supply_id == supply_id

        if period:
            base_filter &= ServiceOrderSupplyDetail.period == period

        filter = base_filter

        return await self.find_all(
            filter=filter,
            limit=limit,
            order_by=order_by,
        )
