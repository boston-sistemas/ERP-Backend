from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.security.models import RolAccesoOperation


class RolAccesoOperationRepository(BaseRepository[RolAccesoOperation]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(RolAccesoOperation, db, flush)
