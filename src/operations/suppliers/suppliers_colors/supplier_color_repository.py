from sqlalchemy import BinaryExpression, ClauseElement, Column, Sequence, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Load, joinedload

from src.core.repository import BaseRepository
from src.operations.models import SupplierColor


class SupplierColorRepository(BaseRepository[SupplierColor]):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(SupplierColor, promec_db, flush)

    def get_load_options(
        self,
        include_color: bool = False,
    ) -> list[Load]:
        options: list[Load] = []

        if include_color:
            options.append(joinedload(SupplierColor.id))

        return options

    async def find_supplier_colors_by_suppliers(
        self,
        supplier_id: str,
        include_color: bool = False,
        filter: BinaryExpression = None,
        limit: int = None,
        offset: int = None,
    ) -> list[SupplierColor]:
        base_filter: list[BinaryExpression] = []
        base_filter.append(SupplierColor.supplier_id == supplier_id)

        filter = (
            and_(*base_filter, filter) if filter is not None else and_(*base_filter)
        )

        options = self.get_load_options(include_color=include_color)

        return await self.find_all(
            filter=filter,
            options=options,
            limit=limit,
            offset=offset,
        )

    async def find_supplier_color_by_id(
        self,
        id: str,
        filter: BinaryExpression = None,
        include_color: bool = False,
    ) -> SupplierColor | None:
        base_filter: list[BinaryExpression] = []
        base_filter.append(SupplierColor.id == id)

        filter = (
            and_(*base_filter, filter) if filter is not None else and_(*base_filter)
        )
        options = self.get_load_options(include_color=include_color)

        return await self.find(
            filter=filter,
            options=options,
        )
