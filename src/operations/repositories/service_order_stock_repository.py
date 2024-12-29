from typing import Sequence, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column
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
        product_code: str,
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
            & (ServiceOrderStock.product_code == product_code)
            & (ServiceOrderStock.storage_code == storage_code)
            & (ServiceOrderStock.reference_number == reference_number)
            & (ServiceOrderStock.period == period)
            & (ServiceOrderStock.item_number == item_number)
        )
        filter = base_filter & filter if filter is not None else base_filter

        return await self.find(filter=filter, options=options, **kwargs)

