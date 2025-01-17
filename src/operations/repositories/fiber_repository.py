from typing import Sequence, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.operations.models import Fiber
from src.security.models import Parameter


class FiberRepository(BaseRepository[Fiber]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Fiber, db, flush)

    @staticmethod
    def include_category() -> Load:
        return joinedload(Fiber.category).load_only(
            Parameter.id, Parameter.value, raiseload=True
        )

    @staticmethod
    def include_denomination() -> Load:
        return joinedload(Fiber.denomination).load_only(
            Parameter.id, Parameter.value, raiseload=True
        )

    def get_load_options(
        self, include_category: bool = False, include_denomination: bool = False
    ) -> list[Load]:
        options: list[Load] = []
        if include_category:
            options.append(self.include_category())
        if include_denomination:
            options.append(self.include_denomination())

        return options

    async def find_fiber_by_id(
        self,
        fiber_id: str,
        include_category: bool = False,
        include_denomination: bool = False,
        **kwargs,
    ) -> Fiber | None:
        options = self.get_load_options(
            include_category=include_category, include_denomination=include_denomination
        )

        fiber = await self.find_by_id(fiber_id, options=options, **kwargs)

        return fiber

    async def find_fibers(
        self,
        filter: BinaryExpression = None,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
        include_category: bool = False,
        include_denomination: bool = False,
        include_inactives: bool = True,
    ) -> list[Fiber]:
        if not include_inactives:
            filter = (
                filter & Fiber.is_active == bool(True)
                if filter
                else Fiber.is_active == bool(True)
            )

        options = self.get_load_options(
            include_category=include_category, include_denomination=include_denomination
        )

        fibers = await self.find_all(filter=filter, options=options, order_by=order_by)

        return fibers
