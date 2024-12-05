from sqlalchemy.ext.asyncio import AsyncSession

from src.security.models import Parameter
from src.security.services import ParameterService


class MultiParameterLoader:
    ids: list[int]

    def __init_subclass__(cls, ids: list[int] = None, **kwargs):
        if ids is None:
            raise TypeError(f"{cls.__name__} requires 'ids' to be defined.")
        cls.ids = ids
        super().__init_subclass__(**kwargs)

    def __init__(self, db: AsyncSession):
        self.service = ParameterService(db=db)

    async def get(self, actives_only: bool = False) -> list[Parameter]:
        result = (
            await self.service.find_parameters_by_ids(
                parameter_ids=self.ids, load_only_value=True, actives_only=actives_only
            )
        ).value
        return result

    async def get_and_mapping(self, actives_only: bool = False) -> dict[int, Parameter]:
        values = await self.get(actives_only=actives_only)
        return {value.id: value for value in values}
