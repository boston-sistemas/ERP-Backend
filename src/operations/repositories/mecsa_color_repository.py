from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import MecsaColor


class MecsaColorRepository(BaseRepository[MecsaColor]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(MecsaColor, db, flush)

    async def find_mecsa_color_by_id(self, color_id: str) -> MecsaColor | None:
        id = {"table": "COL", "id": color_id}
        return await self.find_by_id(id=id)

    async def find_mecsa_colors(
        self, filter: BinaryExpression = None, exclude_legacy: bool = False
    ) -> list[MecsaColor]:
        base_filter = MecsaColor.table == "COL"
        filter = base_filter & filter if filter is not None else base_filter

        mecsa_colors = await self.find_all(filter=filter)

        return (
            [color for color in mecsa_colors if color.id.isdigit()]
            if exclude_legacy
            else mecsa_colors
        )
