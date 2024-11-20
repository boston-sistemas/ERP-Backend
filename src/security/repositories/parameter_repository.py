from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.security.models import Parameter


class ParameterRepository(BaseRepository[Parameter]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Parameter, db, flush)

    @staticmethod
    def include_category() -> Load:
        return joinedload(Parameter.category)

    async def find_parameter_by_id(
        self, parameter_id: int, include_category=False, **kwargs
    ) -> Parameter | None:
        options: list[Load] = []

        if include_category:
            options.append(self.include_category())

        parameter = await self.find_by_id(parameter_id, options=options, **kwargs)

        return parameter
