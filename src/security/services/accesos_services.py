from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.security.models import Acceso


class AccessService:
    def __init__(self, db: AsyncSession, commit: bool = True) -> None:
        self.db = db
        self.commit = commit

    async def read_access(self) -> list[Acceso]:
        stmt = select(Acceso)
        result = await self.db.execute(stmt)
        return result.scalars().all()
