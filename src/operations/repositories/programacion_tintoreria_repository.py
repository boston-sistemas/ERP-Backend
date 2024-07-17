from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import ProgramacionTintoreria


class ProgramacionTintoreriaRepository(BaseRepository[ProgramacionTintoreria]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(ProgramacionTintoreria, db, flush)
