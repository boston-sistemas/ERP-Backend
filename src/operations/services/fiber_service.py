from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import FIBER_NOT_FOUND_FAILURE
from src.operations.models import Fiber
from src.operations.repositories import FiberRepository
from src.operations.schemas import FiberCompleteListSchema, FiberCompleteSchema

from .mecsa_color_service import MecsaColorService


class FiberService:
    def __init__(self, db: AsyncSession, promec_db: AsyncSession):
        self.repository = FiberRepository(db=db)
        self.mecsa_color_service = MecsaColorService(db=promec_db)

    async def _assign_colors_to_fibers(self, fibers: list[Fiber]) -> None:
        color_ids = {fiber.color_id for fiber in fibers if fiber.color_id is not None}

        if not color_ids:
            return None

        color_mapping = await self.mecsa_color_service.map_colors_by_ids(color_ids)

        for fiber in fibers:
            fiber.color = color_mapping.get(fiber.color_id, None)

    async def read_fiber(
        self, fiber_id: str, include_category: bool = False, include_color: bool = False
    ) -> Result[FiberCompleteSchema, CustomException]:
        fiber = await self.repository.find_fiber_by_id(
            fiber_id=fiber_id, include_category=include_category
        )

        if fiber is None:
            return FIBER_NOT_FOUND_FAILURE

        if include_color:
            await self._assign_colors_to_fibers(fibers=[fiber])

        return Success(FiberCompleteSchema.model_validate(fiber))

    async def read_fibers(self) -> Result[FiberCompleteListSchema, CustomException]:
        fibers = await self.repository.find_all(
            options=(self.repository.include_category(),)
        )
        await self._assign_colors_to_fibers(fibers=fibers)

        return Success(FiberCompleteListSchema(fibers=fibers))
