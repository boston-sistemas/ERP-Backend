from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import FabricYarn


class FabricRecipeRepository(BaseRepository[FabricYarn]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(FabricYarn, db, flush)

    async def find_fabrics_by_recipe(self, yarn_ids: list[str]) -> list[str]:
        stmt = (
            select(FabricYarn.fabric_id)
            .where(FabricYarn.yarn_id.in_(yarn_ids))
            .group_by(FabricYarn.fabric_id)
            .having(func.count(FabricYarn.yarn_id) >= len(yarn_ids))
        )

        return (await self.db.scalars(stmt)).all()
