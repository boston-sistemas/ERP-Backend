from typing import Sequence, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import ProductInventory


class ProductInventoryRepository(BaseRepository[ProductInventory]):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(ProductInventory, promec_db, flush)

    async def find_product_inventory_by_product_code_and_storage_code(
        self,
        product_code1: str,
        storage_code: str,
        period: int,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        **kwargs,
    ) -> ProductInventory | None:
        base_filter = (
            (ProductInventory.company_code == MECSA_COMPANY_CODE)
            & (ProductInventory.product_code1 == product_code1)
            & (ProductInventory.storage_code == storage_code)
            & (ProductInventory.period == period)
        )
        filter = base_filter & filter if filter is not None else base_filter

        return await self.find(filter=filter, options=options, **kwargs)

    async def find_products_inventory_by_product_code(
        self,
        product_code1: str,
        period: int,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        apply_unique: bool = False,
        limit: int = None,
        offset: int = None,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
    ) -> list[ProductInventory]:
        base_filter = (
            (ProductInventory.company_code == MECSA_COMPANY_CODE)
            & (ProductInventory.product_code1 == product_code1)
            & (ProductInventory.period == period)
        )
        filter = base_filter & filter if filter is not None else base_filter

        return await self.find_all(
            filter=filter,
            options=options,
            apply_unique=apply_unique,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )
