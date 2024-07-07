from sqlalchemy.ext.asyncio import AsyncSession

from src.security.models import Acceso
from src.security.repositories import AccesoRepository


class AccesoService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = AccesoRepository(db)

    async def read_accesos(self) -> list[Acceso]:
        return await self.repository.find_all()
