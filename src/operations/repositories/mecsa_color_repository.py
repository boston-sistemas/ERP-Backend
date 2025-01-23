from typing import Sequence, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import ACTIVE_STATUS_PROMEC
from src.core.repository import BaseRepository
from src.operations.models import MecsaColor


class MecsaColorRepository(BaseRepository[MecsaColor]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(MecsaColor, db, flush)

    async def find_mecsa_color_by_id(self, color_id: str) -> MecsaColor | None:
        return await self.find(filter=MecsaColor.id == color_id)

    async def find_mecsa_colors(
        self,
        filter: BinaryExpression = None,
        include_inactives: bool = True,
        exclude_legacy: bool = False,
        offset: int = None,
        limit: int = None,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
    ) -> list[MecsaColor]:
        if not include_inactives:
            filter = (
                filter & (MecsaColor.is_active == ACTIVE_STATUS_PROMEC)
                if filter
                else (MecsaColor.is_active == ACTIVE_STATUS_PROMEC)
            )

        mecsa_colors = await self.find_all(
            filter=filter, offset=offset, limit=limit, order_by=order_by
        )
        return (
            [color for color in mecsa_colors if color.id.isdigit()]
            if exclude_legacy
            else mecsa_colors
        )
