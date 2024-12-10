from typing import Sequence

from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import InventoryItem


class InventoryItemRepository(BaseRepository[InventoryItem]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(InventoryItem, db, flush)

    async def find_item_by_id(
        self, id: str, options: Sequence[Load] = None, **kwargs
    ) -> InventoryItem | None:
        id = {"company_code": MECSA_COMPANY_CODE, "id": id}
        return await self.find_by_id(id=id, options=options, **kwargs)

    async def find_items(
        self,
        filter: BinaryExpression = None,
        exclude_legacy: bool = False,
        options: Sequence[Load] = None,
        apply_unique: bool = False,
    ) -> list[InventoryItem]:
        base_filter = InventoryItem.company_code == MECSA_COMPANY_CODE
        filter = base_filter & filter if filter is not None else base_filter

        inventory_items = await self.find_all(
            filter=filter, options=options, apply_unique=apply_unique
        )

        return (
            [item for item in inventory_items if item.id.isdigit()]
            if exclude_legacy
            else inventory_items
        )
