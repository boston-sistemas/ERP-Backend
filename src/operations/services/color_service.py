from sqlalchemy.ext.asyncio import AsyncSession

from src.operations.models import Color
from src.operations.repositories import ColorRepository


class ColorService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = ColorRepository(db)

    async def read_colores(self) -> list[Color]:
        return await self.repository.find_all()
