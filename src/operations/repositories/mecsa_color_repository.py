from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import MecsaColor


class MecsaColorRepository(BaseRepository[MecsaColor]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(MecsaColor, db, flush)
