from sqlalchemy.ext.asyncio import AsyncSession

from src.security.models import Parameter
from src.security.repositories import ParameterRepository


class MultiParameterLoader:
    ids: list[int]

    def __init_subclass__(cls, ids: list[int] = None, **kwargs):
        if ids is None:
            raise TypeError(f"{cls.__name__} requires 'ids' to be defined.")
        cls.ids = ids
        super().__init_subclass__(**kwargs)

    def __init__(self, db: AsyncSession):
        self.repo = ParameterRepository(db=db)

    async def get(self, actives_only: bool = False) -> list[Parameter]:
        filter = Parameter.id.in_(self.ids)
        if actives_only:
            filter = filter & (Parameter.is_active)

        result = await self.repo.find_all(
            filter=filter, options=(self.repo.load_only_value(),)
        )

        return result

    async def get_and_mapping(self, actives_only: bool = False) -> dict[int, Parameter]:
        values = await self.get(actives_only=actives_only)
        return {value.id: value for value in values}
