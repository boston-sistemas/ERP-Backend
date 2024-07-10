from sqlalchemy.ext.asyncio import AsyncSession
from src.core.repository import BaseRepository
from src.security.models import AuthToken


class AuthTokenRepository(BaseRepository[AuthToken]):
    def __init__(self, db: AsyncSession, commit: bool = True) -> None:
        super().__init__(AuthToken, db, commit)
