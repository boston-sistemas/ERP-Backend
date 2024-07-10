from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import OrdenServicioTintoreria


class OrdenServicioTintoreriaRepository(BaseRepository[OrdenServicioTintoreria]):
    def __init__(self, db: AsyncSession, commit: bool = True) -> None:
        super().__init__(OrdenServicioTintoreria, db, commit)
