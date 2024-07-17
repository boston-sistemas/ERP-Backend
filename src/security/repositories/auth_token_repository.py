from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.security.models import AuthToken


class AuthTokenRepository(BaseRepository[AuthToken]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(AuthToken, db, flush)
