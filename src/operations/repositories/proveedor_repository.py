from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import Proveedor


class ProveedorRepository(BaseRepository[Proveedor]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Proveedor, db, flush)
