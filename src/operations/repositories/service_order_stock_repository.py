from typing import Sequence

from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import ServiceOrderStock


class ServiceOrderStockRepository(BaseRepository[ServiceOrderStock]):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(ServiceOrderStock, promec_db, flush)

    async def find_service_order_stock_by_product_code_and_storage_code_and_reference_number_and_item_number(
        self,
        product_code1: str,
        storage_code: str,
        reference_number: str,
        item_number: int,
        period: int,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        **kwargs,
    ) -> ServiceOrderStock | None:
        base_filter = (
            (ServiceOrderStock.company_code == MECSA_COMPANY_CODE)
            & (ServiceOrderStock.product_code1 == product_code1)
            & (ServiceOrderStock.storage_code == storage_code)
            & (ServiceOrderStock.reference_number == reference_number)
            & (ServiceOrderStock.period == period)
            & (ServiceOrderStock.item_number == item_number)
        )
        filter = base_filter & filter if filter is not None else base_filter

        return await self.find(filter=filter, options=options, **kwargs)

    async def find_service_order_stocks_by_service_order_id_and_storage_code(
        self,
        storage_code: str,
        service_order_id: str,
        period: int,
    ) -> list[ServiceOrderStock]:
        base_filter = (
            (ServiceOrderStock.company_code == MECSA_COMPANY_CODE)
            & (ServiceOrderStock.reference_number == service_order_id)
            & (ServiceOrderStock.period == period)
            & (ServiceOrderStock.storage_code == storage_code)
        )

        filter = base_filter

        return await self.find_all(
            filter=filter,
            order_by=ServiceOrderStock.item_number.asc(),
        )

    async def find_service_order_stocks_by_service_order_id_and_storage_code_and_product_id(
        self,
        storage_code: str,
        service_order_id: str,
        product_id: str,
        period: int,
        limit: int = None,
        order_by: Sequence = None,
    ) -> list[ServiceOrderStock]:
        base_filter = (
            (ServiceOrderStock.company_code == MECSA_COMPANY_CODE)
            & (ServiceOrderStock.reference_number == service_order_id)
            & (ServiceOrderStock.period == period)
            & (ServiceOrderStock.storage_code == storage_code)
            & (ServiceOrderStock.product_code1 == product_id)
        )

        filter = base_filter

        return await self.find_all(
            filter=filter,
            limit=limit,
            order_by=order_by,
        )
