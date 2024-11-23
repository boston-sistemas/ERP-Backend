from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.result import Result, Success
from src.operations.failures import (
    COLOR_DISABLED_WHEN_CREATING_FIBER_FAILURE,
    COLOR_NOT_FOUND_WHEN_CREATING_FIBER_FAILURE,
    FIBER_ALREADY_EXISTS_FAILURE,
    FIBER_CATEGORY_DISABLED_WHEN_CREATING_FIBER_FAILURE,
    FIBER_CATEGORY_NOT_FOUND_WHEN_CREATING_FIBER_FAILURE,
    FIBER_NOT_FOUND_FAILURE,
)
from src.operations.models import Fiber
from src.operations.repositories import FiberRepository
from src.operations.schemas import (
    FiberCompleteListSchema,
    FiberCompleteSchema,
    FiberCreateSchema,
)
from src.operations.sequences import product_id_seq
from src.security.loaders import FiberCategories
from src.security.services import ParameterService

from .mecsa_color_service import MecsaColorService


class FiberService:
    def __init__(self, db: AsyncSession, promec_db: AsyncSession):
        self.repository = FiberRepository(db=db)
        self.parameter_service = ParameterService(db=db)
        self.mecsa_color_service = MecsaColorService(promec_db=promec_db)
        self.product_sequence = SequenceRepository(
            sequence=product_id_seq, db=promec_db
        )
        self.fiber_categories = FiberCategories(db=db)

    async def _assign_colors_to_fibers(self, fibers: list[Fiber]) -> None:
        color_ids = {fiber.color_id for fiber in fibers if fiber.color_id is not None}

        if not color_ids:
            return None

        color_mapping = await self.mecsa_color_service.map_colors_by_ids(color_ids)

        for fiber in fibers:
            fiber.color = color_mapping.get(fiber.color_id, None)

    async def _is_fiber_unique(
        self,
        category_id: int,
        denomination: str | None,
        origin: str | None,
        color_id: str | None,
    ) -> bool:
        fiber = await self.repository.find(
            (Fiber.category_id == category_id)
            & (Fiber.denomination == denomination)
            & (Fiber.origin == origin)
            & (Fiber.color_id == color_id)
        )
        return fiber is None

    async def _validate_fiber_data(
        self,
        category_id: int | None = None,
        color_id: str | None = None,
        action: str = "create",
    ) -> Result[None, CustomException]:
        failures = {
            "create": {
                "category_not_found": FIBER_CATEGORY_NOT_FOUND_WHEN_CREATING_FIBER_FAILURE,
                "category_disabled": FIBER_CATEGORY_DISABLED_WHEN_CREATING_FIBER_FAILURE,
                "color_not_found": COLOR_NOT_FOUND_WHEN_CREATING_FIBER_FAILURE,
                "color_disabled": COLOR_DISABLED_WHEN_CREATING_FIBER_FAILURE,
            }
        }
        current_failures = failures.get(action, {})

        if category_id is not None:
            categories = await self.fiber_categories.get()
            category_result = next(
                (category for category in categories if category.id == category_id),
                None,
            )
            if category_result is None:
                return current_failures["category_not_found"]
            if not category_result.is_active:
                return current_failures["category_disabled"]

        if color_id is not None:
            color_result = await self.mecsa_color_service.read_mecsa_color(color_id)
            if color_result.is_failure:
                return current_failures["color_not_found"]
            if color_result.value.is_active != "A":
                return current_failures["color_disabled"]

        return Success(None)

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

    async def create_fiber(
        self, form: FiberCreateSchema
    ) -> Result[Fiber, CustomException]:
        validation_result = await self._validate_fiber_data(
            category_id=form.category_id, color_id=form.color_id
        )
        if validation_result.is_failure:
            return validation_result

        fiber_dict = form.model_dump()
        if not (await self._is_fiber_unique(**fiber_dict)):
            return FIBER_ALREADY_EXISTS_FAILURE

        fiber_id = await self.product_sequence.next_value()
        fiber = Fiber(**fiber_dict, id=str(fiber_id))

        await self.repository.save(fiber)

        return Success(fiber)
