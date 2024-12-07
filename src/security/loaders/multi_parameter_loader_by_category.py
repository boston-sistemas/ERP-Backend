from sqlalchemy.ext.asyncio import AsyncSession

from src.core.result import Result, Success
from src.security.failures import PARAMETER_NOT_FOUND_FAILURE
from src.security.models import Parameter
from src.security.services import ParameterService


class MultiParameterLoaderByCategory:
    param_category_id: int

    def __init_subclass__(cls, param_category_id: int = None, **kwargs):
        if param_category_id is None:
            raise TypeError(
                f"{cls.__name__} requires 'param_category_id' to be defined."
            )
        cls.param_category_id = param_category_id
        super().__init_subclass__(**kwargs)

    def __init__(self, db: AsyncSession):
        self.service = ParameterService(db=db)

    async def get(self, actives_only: bool = False) -> list[Parameter]:
        result = await self.service.read_parameters_by_category(
            parameter_category_id=self.param_category_id,
            load_only_value=True,
            actives_only=actives_only,
        )
        return result.value

    async def get_and_mapping(self, actives_only: bool = False) -> dict[int, Parameter]:
        values = await self.get(actives_only=actives_only)
        return {value.id: value for value in values}

    async def validate(self, id: int) -> Result[Parameter, None]:
        parameter_result = await self.service.read_parameter(parameter_id=id)
        if parameter_result.is_failure:
            return PARAMETER_NOT_FOUND_FAILURE

        parameter: Parameter = parameter_result.value
        if parameter.category_id != self.param_category_id:
            return PARAMETER_NOT_FOUND_FAILURE

        return Success(parameter)
