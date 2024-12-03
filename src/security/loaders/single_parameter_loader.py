from sqlalchemy.ext.asyncio import AsyncSession

from src.security.models import Parameter
from src.security.services import ParameterService


class SingleParameterLoader:
    id: int

    def __init_subclass__(cls, id: int = None, **kwargs):
        if id is None:
            raise TypeError(f"{cls.__name__} requires 'id' to be defined.")
        cls.id = id
        super().__init_subclass__(**kwargs)

    def __init__(self, db: AsyncSession):
        self.service = ParameterService(db=db)

    async def get(
        self,
    ) -> Parameter:
        result = await self.service.read_parameter(
            parameter_id=self.id, load_only_value=True
        )
        if result.success:
            return result.value

        raise result.error
