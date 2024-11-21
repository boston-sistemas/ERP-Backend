from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.operations.models import Fiber


class FiberRepository(BaseRepository[Fiber]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Fiber, db, flush)

    @staticmethod
    def include_category() -> Load:
        return joinedload(Fiber.category)

    async def find_fiber_by_id(
        self, fiber_id: str, include_category: bool = False, **kwargs
    ) -> Fiber | None:
        options: list[Load] = []

        if include_category:
            options.append(self.include_category())

        fiber = await self.find_by_id(fiber_id, options=options, **kwargs)

        return fiber
