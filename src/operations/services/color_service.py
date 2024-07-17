from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import ColorFailures
from src.operations.models import Color
from src.operations.repositories import ColorRepository


class ColorService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = ColorRepository(db)

    async def read_color(self, color_id) -> Result[Color, CustomException]:
        color = await self.repository.find_by_id(color_id)
        if color is not None:
            return Success(color)
        return ColorFailures.COLOR_NOT_FOUND_FAILURE

    async def read_colores(self) -> list[Color]:
        return await self.repository.find_all()
