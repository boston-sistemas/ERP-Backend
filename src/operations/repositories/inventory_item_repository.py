from typing import Sequence, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import ACTIVE_STATUS_PROMEC, MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import InventoryItem


class InventoryItemRepository(BaseRepository[InventoryItem]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(InventoryItem, db, flush)

    @staticmethod
    def get_fields() -> tuple:
        return (
            InventoryItem.id,
            InventoryItem.family_id,
            InventoryItem.subfamily_id,
            InventoryItem.base_unit_code,
            InventoryItem.inventory_unit_code,
            InventoryItem.purchase_unit_code,
            InventoryItem.description,
            InventoryItem.purchase_description,
            InventoryItem.barcode,
            InventoryItem.is_active,
        )

    async def find_item_by_id(
        self, id: str, options: Sequence[Load] = None, **kwargs
    ) -> InventoryItem | None:
        id = {"company_code": MECSA_COMPANY_CODE, "id": id}
        return await self.find_by_id(id=id, options=options, **kwargs)

    async def find_items(
        self,
        filter: BinaryExpression = None,
        include_inactives: bool = True,
        exclude_legacy: bool = False,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
        options: Sequence[Load] = None,
        apply_unique: bool = False,
    ) -> list[InventoryItem]:
        base_filter = InventoryItem.company_code == MECSA_COMPANY_CODE
        filter = base_filter & filter if filter is not None else base_filter

        if not include_inactives:
            filter = filter & (InventoryItem.is_active == ACTIVE_STATUS_PROMEC)

        inventory_items = await self.find_all(
            filter=filter, order_by=order_by, options=options, apply_unique=apply_unique
        )

        return (
            [item for item in inventory_items if item.id.isdigit()]
            if exclude_legacy
            else inventory_items
        )
