from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.security.models import ModuloSistema


class ModuloSistemaRepository(BaseRepository[ModuloSistema]):
    def __init__(self, db: AsyncSession, commit: bool = True) -> None:
        super().__init__(ModuloSistema, db, commit)