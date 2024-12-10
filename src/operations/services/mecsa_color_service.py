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

    async def validate_mecsa_color_data(
        self,
        name: str | None = None,
        sku: str | None = None,
        hexadecimal: str | None = None,
    ):
        name_exists = False
        if name is not None:
            colors = await self.repository.find_all(
                (MecsaColor.table == "COL") & (MecsaColor.name == name)
            )

            for color in colors:
                if color.id.isdigit() and color.name == name:
                    name_exists = True
                    break

        if name_exists:
            return MECSA_COLOR_NAME_ALREADY_EXISTS_FAILURE(name)

        sku_exists = False
        if sku is not None:
            colors = await self.repository.find_all(
                (MecsaColor.table == "COL") & (MecsaColor.sku == sku)
            )

            for color in colors:
                if color.id.isdigit() and color.name == name:
                    sku_exists = True
                    break

        if sku_exists:
            return MECSA_COLOR_SKU_ALREADY_EXISTS_FAILURE(sku)

        # TODO: Validate the hexadecimal format

        return Success(None)

    async def create_mecsa_color(
        self, form: MecsaColorCreateSchema
    ) -> Result[MecsaColor, CustomException]:
        validation_result = await self.validate_mecsa_color_data(
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
        mecsa_color = await self.repository.find_by_id({"table": "COL", "id": color_id})
        if mecsa_color is not None:
            return Success(mecsa_color)
        return MECSA_COLOR_NOT_FOUND_FAILURE

    async def read_mecsa_colors(self) -> Result[list[MecsaColor], CustomException]:
        mecsa_colors = await self.repository.find_all(MecsaColor.table == "COL")
        return Success(
            [mecsa_color for mecsa_color in mecsa_colors if mecsa_color.id.isdigit()]
        )

    async def map_colors_by_ids(self, color_ids: set[str]) -> dict[str, MecsaColor]:
        if not color_ids:
            return {}

        colors = await self.repository.find_all(
            (MecsaColor.table == "COL") & MecsaColor.id.in_(color_ids)
        )
        return {color.id: color for color in colors}
