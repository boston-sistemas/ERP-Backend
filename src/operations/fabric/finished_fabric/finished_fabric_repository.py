from typing import Sequence, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.strategy_options import Load

from src.operations.constants import FABRIC_FAMILY_ID
from src.operations.models import FabricYarn, InventoryItem
from src.operations.repositories import InventoryItemRepository


class FinishedFabricRepository(InventoryItemRepository):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(db, flush)

    @staticmethod
    def get_fabric_fields() -> tuple:
        return (
            *InventoryItemRepository.get_fields(),
            InventoryItem.field1,
            InventoryItem.field2,
            InventoryItem.field3,
            InventoryItem.field4,
            InventoryItem.field5,
            InventoryItem.field6,
        )

    @staticmethod
    def include_color() -> Load:
        return joinedload(InventoryItem.fabric_color)

    @staticmethod
    def include_recipe() -> Load:
        return joinedload(InventoryItem.fabric_recipe).load_only(
            FabricYarn.fabric_id,
            FabricYarn.yarn_id,
            FabricYarn.proportion,
            FabricYarn.num_plies,
        )

    def get_load_options(
        self, include_color: bool = False, include_recipe: bool = False
    ) -> list[Load]:
        options: list[Load] = [load_only(*self.get_fabric_fields())]

        if include_color:
            options.append(self.include_color())

        if include_recipe:
            options.append(self.include_recipe())

        return options

    async def find_fabric_by_id(
        self,
        fabric_id: str,
        include_color: bool = False,
        include_recipe: bool = False,
    ) -> InventoryItem | None:
        options = self.get_load_options(
            include_color=include_color, include_recipe=include_recipe
        )

        fabric = await self.find_item_by_id(id=fabric_id, options=options)

        return (
            fabric
            if fabric is not None and fabric.family_id == FABRIC_FAMILY_ID
            else None
        )

    async def find_fabrics(
        self,
        filter: BinaryExpression = None,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
        include_inactives: bool = True,
        include_color: bool = False,
        include_recipe: bool = False,
        exclude_legacy: bool = False,
    ) -> list[InventoryItem]:
        base_filter = InventoryItem.family_id == FABRIC_FAMILY_ID
        filter = base_filter & filter if filter is not None else base_filter

        options = self.get_load_options(
            include_color=include_color, include_recipe=include_recipe
        )

        fabrics = await self.find_items(
            filter=filter,
            include_inactives=include_inactives,
            exclude_legacy=exclude_legacy,
            order_by=order_by,
            options=options,
            apply_unique=include_recipe,
        )

        return fabrics
