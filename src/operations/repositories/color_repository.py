from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import Color


class ColorRepository(BaseRepository[Color]):
    def __init__(self, db: AsyncSession, commit: bool = True) -> None:
        super().__init__(Color, db, commit)
