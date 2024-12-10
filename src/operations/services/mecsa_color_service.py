from sqlalchemy.ext.asyncio import AsyncSession

from operations.schemas.mecsa_color_schema import MecsaColorCreateSchema
from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.result import Result, Success
from src.operations.failures import (
    MECSA_COLOR_NAME_ALREADY_EXISTS_FAILURE,
    MECSA_COLOR_NOT_FOUND_FAILURE,
    MECSA_COLOR_SKU_ALREADY_EXISTS_FAILURE,
)
from src.operations.models import MecsaColor
from src.operations.repositories import MecsaColorRepository
from src.operations.sequences import color_id_seq


class MecsaColorService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.repository = MecsaColorRepository(db=promec_db)
        self.color_sequence = SequenceRepository(sequence=color_id_seq, db=promec_db)

    async def _validate_mecsa_color_data(
        self,
        name: str | None = None,
        sku: str | None = None,
        hexadecimal: str | None = None,
    ) -> Result[None, CustomException]:
        name_exists = False
        if name is not None:
            colors = await self.repository.find_mecsa_colors(
                filter=MecsaColor.name == name, exclude_legacy=True
            )
            name_exists = any(color.name == name for color in colors)

        if name_exists:
            return MECSA_COLOR_NAME_ALREADY_EXISTS_FAILURE(name)

        sku_exists = False
        if sku is not None:
            colors = await self.repository.find_mecsa_colors(
                filter=MecsaColor.sku == sku
            )
            sku_exists = any(color.sku == sku for color in colors)

        if sku_exists:
            return MECSA_COLOR_SKU_ALREADY_EXISTS_FAILURE(sku)

        # TODO: Validate the hexadecimal format

        return Success(None)

    async def create_mecsa_color(
        self, form: MecsaColorCreateSchema
    ) -> Result[MecsaColor, CustomException]:
        validation_result = await self._validate_mecsa_color_data(
            name=form.name, sku=form.sku, hexadecimal=form.hexadecimal
        )
        if validation_result.is_failure:
            return validation_result

        mecsa_color_id = await self.color_sequence.next_value()
        mecsa_color = MecsaColor(id=mecsa_color_id, **form.model_dump())

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
        self, exclude_legacy: bool = False
    ) -> Result[list[MecsaColor], CustomException]:
        mecsa_colors = await self.repository.find_mecsa_colors(
            exclude_legacy=exclude_legacy
        )
        return Success(mecsa_colors)

    async def find_mecsa_colors_by_ids(
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
            await self.find_mecsa_colors_by_ids(mecsa_color_ids=color_ids)
        ).value

        return Success({mecsa_color.id: mecsa_color for mecsa_color in mecsa_colors})
