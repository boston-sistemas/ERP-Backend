from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.security.models import RolAcceso


class RolAccesoRepository(BaseRepository[RolAcceso]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(RolAcceso, db, flush)
