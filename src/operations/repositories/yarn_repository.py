from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.strategy_options import Load

from src.operations.constants import SUPPLY_FAMILY_ID, YARN_SUBFAMILY_ID
from src.operations.models import InventoryItem

from .inventory_item_repository import InventoryItemRepository


class YarnRepository(InventoryItemRepository):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(db, flush)

    @staticmethod
    def get_yarn_fields() -> tuple:
        return (
            InventoryItem.id,
            InventoryItem.family_id,
            InventoryItem.subfamily_id,
            InventoryItem.base_unit_code,
            InventoryItem.inventory_unit_code,
            InventoryItem.purchase_unit_code,
            InventoryItem.description,
            InventoryItem.purchase_description,
            InventoryItem.field1,
            InventoryItem.field2,
            InventoryItem.field3,
            InventoryItem.field4,
            InventoryItem.is_active,
        )

    @staticmethod
    def include_color() -> Load:
        return joinedload(InventoryItem.yarn_color)

    def get_load_options(self, include_color: bool = False) -> list[Load]:
        options: list[Load] = []
        if include_color:
            options.append(self.include_color())

        options.append(load_only(*self.get_yarn_fields()))
        return options

    async def find_yarn_by_id(
        self, yarn_id: str, include_color: bool = False
    ) -> InventoryItem | None:
        options = self.get_load_options(include_color=include_color)

        yarn = await self.find_item_by_id(id=yarn_id, options=options)

        return (
            yarn
            if yarn is not None
            and yarn.family_id == SUPPLY_FAMILY_ID
            and yarn.subfamily_id == YARN_SUBFAMILY_ID
            else None
        )

    async def find_yarns(
        self, filter: BinaryExpression = None, include_color: bool = False
    ) -> list[InventoryItem]:
        base_filter = (InventoryItem.family_id == SUPPLY_FAMILY_ID) & (
            InventoryItem.subfamily_id == YARN_SUBFAMILY_ID
        )
        filter = base_filter & filter if filter is not None else base_filter
        options = self.get_load_options(include_color=include_color)

        yarns = await self.find_items(filter=filter, options=options)

        return yarns
