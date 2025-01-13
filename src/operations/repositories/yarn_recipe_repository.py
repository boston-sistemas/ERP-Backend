from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.operations.models import YarnFiber


class YarnRecipeRepository(BaseRepository[YarnFiber]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(YarnFiber, db, flush)

    @staticmethod
    def include_fiber_instance() -> Load:
        return joinedload(YarnFiber.fiber)

    async def get_unique_fiber_ids_from_recipes(self, yarn_ids: list[str]) -> list[str]:
        stmt = (
            select(YarnFiber.fiber_id).distinct().where(YarnFiber.yarn_id.in_(yarn_ids))
        )
        result = await self.db.scalars(stmt).all()

        return result

    async def find_yarn_ids_by_recipe(self, fiber_ids: list[str]) -> list[str]:
        stmt = (
            select(YarnFiber.yarn_id)
            .where(YarnFiber.fiber_id.in_(fiber_ids))
            .group_by(YarnFiber.yarn_id)
            .having(func.count(YarnFiber.fiber_id) >= len(fiber_ids))
        )

        return (await self.db.scalars(stmt)).all()
