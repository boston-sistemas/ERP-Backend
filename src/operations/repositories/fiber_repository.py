from sqlalchemy import BinaryExpression
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

    def get_load_options(self, include_category: bool = False) -> list[Load]:
        options: list[Load] = []
        if include_category:
            options.append(self.include_category())

        return options

    async def find_fiber_by_id(
        self, fiber_id: str, include_category: bool = False, **kwargs
    ) -> Fiber | None:
        options = self.get_load_options(include_category=include_category)

        fiber = await self.find_by_id(fiber_id, options=options, **kwargs)

        return fiber

    async def find_fibers(
        self, filter: BinaryExpression = None, include_category: bool = False
    ) -> list[Fiber]:
        options = self.get_load_options(include_category=include_category)

        fibers = await self.find_all(filter=filter, options=options)

        return fibers
