from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.operations.models import BaseUnit, DerivedUnit
from src.operations.repositories import BaseUnitRepository


class UnitService:
    def __init__(self, promec_db: AsyncSession):
        self.repository = BaseUnitRepository(db=promec_db)
        self.derived_units_repository = BaseRepository[DerivedUnit]

    async def read_base_unit(
        self, code: str, include_derived_units: bool = False
    ) -> Result[BaseUnit, CustomException]:
        base_unit = await self.repository.find_base_unit_by_code(
            code=code, include_derived_units=include_derived_units
        )
        if base_unit is not None:
            return Success(base_unit)

        return None

    async def read_base_units(
        self, include_derived_units: bool = False
    ) -> Result[list[BaseUnit], CustomException]:
        return Success(
            await self.repository.find_base_units(
                include_derived_units=include_derived_units
            )
        )

    async def read_derived_units_by_base_code(self, base_code: str):
        result = await self.read_base_unit(code=base_code, include_derived_units=True)
        if result.is_failure:
            return result

        base_unit = result.value
        return Success(base_unit.derived_units)
