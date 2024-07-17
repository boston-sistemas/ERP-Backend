from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.security.models import Acceso


class AccesoRepository(BaseRepository[Acceso]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Acceso, db, flush)
