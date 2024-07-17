from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.security.models import UsuarioRol


class UserRolRepository(BaseRepository[UsuarioRol]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(UsuarioRol, db, flush)
