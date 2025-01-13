from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.result import Result, Success
from src.core.utils import is_active_status
from src.operations.failures import (
    CATEGORY_DISABLED_FIBER_VALIDATION_FAILURE,
    CATEGORY_NOT_FOUND_FIBER_VALIDATION_FAILURE,
    CATEGORY_NULL_FIBER_VALIDATION_FAILURE,
    FIBER_ALREADY_EXISTS_FAILURE,
    FIBER_NOT_FOUND_FAILURE,
    MECSA_COLOR_DISABLED_FAILURE,
)
from src.operations.models import Fiber
from src.operations.repositories import FiberRepository
from src.operations.schemas import FiberCreateSchema, FiberUpdateSchema
from src.operations.sequences import product_id_seq
from src.security.loaders import FiberCategories

from .mecsa_color_service import MecsaColorService


class FiberService:
    def __init__(self, db: AsyncSession, promec_db: AsyncSession):
        self.repository = FiberRepository(db=db)
        self.mecsa_color_service = MecsaColorService(promec_db=promec_db)
        self.product_sequence = SequenceRepository(
            sequence=product_id_seq, db=promec_db
        )
        self.fiber_categories = FiberCategories(db=db)

    async def _assign_color_to_fibers(self, fibers: list[Fiber]) -> None:
        color_ids = {fiber.color_id for fiber in fibers if fiber.color_id is not None}

        if not color_ids:
            return None

        color_mapping = (
            await self.mecsa_color_service.map_colors_by_ids(color_ids)
        ).value

        for fiber in fibers:
            fiber.color = color_mapping.get(fiber.color_id, None)

    async def _is_fiber_unique(
        self,
        category_id: int,
        denomination: str | None,
        origin: str | None,
        color_id: str | None,
        current_fiber: Fiber | None = None,
    ) -> bool:
        _fibers = await self.repository.find_all(
            (Fiber.category_id == category_id)
            & (Fiber.denomination == denomination)
            & (Fiber.origin == origin)
            & (Fiber.color_id == color_id)
        )

        fibers = (
            _fibers
            if current_fiber is None
            else [fiber for fiber in _fibers if fiber != current_fiber]
        )
        return len(fibers) == 0

    async def _validate_fiber_data(
        self,
        category_id: int | None = None,
        color_id: str | None = None,
        **kwargs,
    ) -> Result[None, CustomException]:
        if category_id is not None:
            result = await self.fiber_categories.validate(id=category_id)
            if result.is_failure:
                return CATEGORY_NOT_FOUND_FIBER_VALIDATION_FAILURE
            if not result.value.is_active:
                return CATEGORY_DISABLED_FIBER_VALIDATION_FAILURE

        if color_id is not None:
            color_result = await self.mecsa_color_service.read_mecsa_color(color_id)
            if color_result.is_failure:
                return color_result
            if not is_active_status(color_result.value.is_active):
                return MECSA_COLOR_DISABLED_FAILURE

        return Success(None)

    async def read_fiber(
        self, fiber_id: str, include_category: bool = False, include_color: bool = False
    ) -> Result[Fiber, CustomException]:
        fiber = await self.repository.find_fiber_by_id(
            fiber_id=fiber_id, include_category=include_category
        )

        if fiber is None:
            return FIBER_NOT_FOUND_FAILURE

        if include_color:
            await self._assign_color_to_fibers(fibers=[fiber])

        return Success(fiber)

    async def read_fibers(
        self,
        include_inactives: bool = False,
        include_category: bool = False,
        include_color: bool = False,
    ) -> Result[list[Fiber], CustomException]:
        fibers = await self.repository.find_fibers(
            filter=Fiber.is_active.is_(True) if not include_inactives else None,
            include_category=include_category,
            order_by=Fiber.id.asc(),
        )

        if include_color:
            await self._assign_color_to_fibers(fibers=fibers)

        return Success(fibers)

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

    async def update_fiber(
        self, fiber_id: str, form: FiberUpdateSchema
    ) -> Result[Fiber, CustomException]:
        fiber_result = await self.read_fiber(fiber_id)
        if fiber_result.is_failure:
            return fiber_result

        fiber: Fiber = fiber_result.value
        fiber_data = form.model_dump(exclude_unset=True)
        if len(fiber_data) == 0:
            return Success(fiber)

        if fiber_data.get("category_id", "") is None:
            return CATEGORY_NULL_FIBER_VALIDATION_FAILURE

        validation_result = await self._validate_fiber_data(**fiber_data)
        if validation_result.is_failure:
            return validation_result

        for key, value in fiber_data.items():
            setattr(fiber, key, value)

        if not (
            await self._is_fiber_unique(
                category_id=fiber.category_id,
                denomination=fiber.denomination,
                origin=fiber.origin,
                color_id=fiber.color_id,
                current_fiber=fiber,
            )
        ):
            return FIBER_ALREADY_EXISTS_FAILURE

        await self.repository.save(fiber)
        return Success(None)

    async def update_status(
        self, fiber_id: str, is_active: bool = True
    ) -> Result[Fiber, CustomException]:
        fiber_result = await self.read_fiber(fiber_id=fiber_id)
        if fiber_result.is_failure:
            return fiber_result

        fiber: Fiber = fiber_result.value
        fiber.is_active = is_active
        await self.repository.save(fiber)

        return Success(fiber)

    async def find_fibers_by_ids(
        self,
        fiber_ids: list[str],
        include_category: bool = False,
        include_color: bool = False,
    ) -> Result[list[Fiber], CustomException]:
        if not fiber_ids:
            return Success([])

        if len(fiber_ids) == 1:
            id = fiber_ids[0]
            result = await self.read_fiber(
                fiber_id=id,
                include_category=include_category,
                include_color=include_color,
            )
            if result.is_success:
                return Success([result.value])

            return Success([])

        fibers = await self.repository.find_fibers(
            filter=Fiber.id.in_(fiber_ids), include_category=include_category
        )

        if include_color:
            await self._assign_color_to_fibers(fibers)

        return Success(fibers)

    async def map_fibers_by_ids(
        self,
        fiber_ids: list[str],
        include_category: bool = False,
        include_color: bool = False,
    ) -> Result[dict[str, Fiber], CustomException]:
        fibers = (
            await self.find_fibers_by_ids(
                fiber_ids=fiber_ids,
                include_category=include_category,
                include_color=include_color,
            )
        ).value

        return Success({fiber.id: fiber for fiber in fibers})
