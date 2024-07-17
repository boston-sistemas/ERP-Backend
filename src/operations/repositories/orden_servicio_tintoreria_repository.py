from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import OrdenServicioTintoreria


class OrdenServicioTintoreriaRepository(BaseRepository[OrdenServicioTintoreria]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(OrdenServicioTintoreria, db, flush)
