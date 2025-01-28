from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.result import Result, Success
from src.core.utils import map_active_status
from src.operations.failures import (
    MECSA_COLOR_NAME_ALREADY_EXISTS_FAILURE,
    MECSA_COLOR_NOT_FOUND_FAILURE,
    MECSA_COLOR_SKU_ALREADY_EXISTS_FAILURE,
)
from src.operations.models import MecsaColor
from src.operations.repositories import MecsaColorRepository
from src.operations.schemas import MecsaColorCreateSchema, MecsaColorUpdateSchema
from src.operations.sequences import color_id_seq


class MecsaColorService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.repository = MecsaColorRepository(db=promec_db)
        self.color_sequence = SequenceRepository(sequence=color_id_seq, db=promec_db)

    async def _validate_mecsa_color_data(
        self,
        name: str = None,
        slug: str = None,
        sku: str = None,
        hexadecimal: str | None = None,
    ) -> Result[None, CustomException]:
        if slug is not None:
            colors = await self.repository.find_mecsa_colors(
                filter=MecsaColor.slug == slug, limit=1, exclude_legacy=True
            )
            if colors:
                return MECSA_COLOR_NAME_ALREADY_EXISTS_FAILURE(name)

        if sku is not None:
            colors = await self.repository.find_mecsa_colors(
                filter=MecsaColor.sku == sku, limit=1, exclude_legacy=True
            )
            if colors:
                return MECSA_COLOR_SKU_ALREADY_EXISTS_FAILURE(sku)

        # TODO: Validate the hexadecimal format

        return Success(None)

    async def create_mecsa_color(
        self, form: MecsaColorCreateSchema
    ) -> Result[MecsaColor, CustomException]:
        color_data = form.model_dump()
        validation_result = await self._validate_mecsa_color_data(**color_data)
        if validation_result.is_failure:
            return validation_result

        mecsa_color_id = await self.color_sequence.next_value()
        mecsa_color = MecsaColor(id=mecsa_color_id, **color_data)

        await self.repository.save(mecsa_color)

        return Success(mecsa_color)

    async def read_mecsa_color(
        self, color_id: str
    ) -> Result[MecsaColor, CustomException]:
        mecsa_color = await self.repository.find_mecsa_color_by_id(color_id=color_id)
        if mecsa_color is not None:
            return Success(mecsa_color)
        return MECSA_COLOR_NOT_FOUND_FAILURE

    async def read_mecsa_colors(
        self, include_inactives: bool = True, exclude_legacy: bool = False
    ) -> Result[list[MecsaColor], CustomException]:
        mecsa_colors = await self.repository.find_mecsa_colors(
            include_inactives=include_inactives,
            exclude_legacy=exclude_legacy,
            order_by=MecsaColor.slug.asc(),
        )
        return Success(mecsa_colors)

    async def read_mecsa_colors_by_ids(
        self, mecsa_color_ids: list[str]
    ) -> Result[list[MecsaColor], CustomException]:
        if not mecsa_color_ids:
            return Success([])

        mecsa_colors = await self.repository.find_mecsa_colors(
            filter=MecsaColor.id.in_(mecsa_color_ids)
        )

        return Success(mecsa_colors)

    async def map_colors_by_ids(
        self, color_ids: list[str]
    ) -> Result[dict[str, MecsaColor], CustomException]:
        mecsa_colors = (
            await self.read_mecsa_colors_by_ids(mecsa_color_ids=color_ids)
        ).value

        return Success({mecsa_color.id: mecsa_color for mecsa_color in mecsa_colors})

    async def update_mecsa_color(
        self, color_id: str, form: MecsaColorUpdateSchema
    ) -> Result[MecsaColor, CustomException]:
        result = await self.read_mecsa_color(color_id=color_id)
        if result.is_failure:
            return result

        color = result.value
        color_data = form.model_dump(exclude_unset=True)

        new_slug = color_data.pop("slug", color.slug)
        new_sku = color_data.pop("sku", color.sku)
        validation_result = await self._validate_mecsa_color_data(
            slug=new_slug if color.slug != new_slug else None,
            sku=new_sku if color.sku != new_sku else None,
            **color_data,
        )
        if validation_result.is_failure:
            return validation_result

        for key, value in color_data.items():
            setattr(color, key, value)

        await self.repository.save(color)

        return Success(color)

    async def update_status(
        self, color_id: str, is_active: bool = True
    ) -> Result[None, CustomException]:
        result = await self.read_mecsa_color(color_id=color_id)
        if result.is_failure:
            return result

        color = result.value
        color.is_active = map_active_status(is_active)
        await self.repository.save(color)

        return Success(None)
