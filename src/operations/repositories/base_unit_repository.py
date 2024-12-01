from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.operations.models import BaseUnit


class BaseUnitRepository(BaseRepository[BaseUnit]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(BaseUnit, db, flush)

    @staticmethod
    def include_derived_units() -> Load:
        return joinedload(BaseUnit.derived_units)

    def get_load_options(self, include_derived_units: bool = False) -> list[Load]:
        options: list[Load] = []

        if include_derived_units:
            options.append(self.include_derived_units())

        return options

    async def find_base_unit_by_code(
        self, code: str, include_derived_units: bool = False
    ) -> BaseUnit | None:
        options = self.get_load_options(include_derived_units=include_derived_units)

        base_unit = await self.find_by_id(code, options=options)

        return base_unit

    async def find_base_units(
        self, filter: BinaryExpression = None, include_derived_units: bool = False
    ) -> list[BaseUnit]:
        options = self.get_load_options(include_derived_units=include_derived_units)

        base_units = await self.find_all(
            filter=filter, options=options, apply_unique=True if options else False
        )

        return base_units
