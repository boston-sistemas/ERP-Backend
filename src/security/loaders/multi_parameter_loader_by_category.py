from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.models import Parameter

from .abstract_loader import AbstractParameterLoader


class MultiParameterLoaderByCategory(AbstractParameterLoader):
    param_category_id: int

    def __init_subclass__(cls, param_category_id: int = None, **kwargs):
        if param_category_id is None:
            raise TypeError(
                f"{cls.__name__} requires 'param_category_id' to be defined."
            )
        cls.param_category_id = param_category_id
        super().__init_subclass__(**kwargs)

    async def get(self, include_inactives: bool = False) -> list[Parameter]:
        parameters = await self.repository.find_parameters(
            filter=Parameter.category_id == self.param_category_id,
            load_only_value=True,
            include_inactives=include_inactives,
        )
        return parameters

    async def get_and_mapping(
        self, include_inactives: bool = False
    ) -> dict[int, Parameter]:
        values = await self.get(include_inactives=include_inactives)
        return {value.id: value for value in values}

    async def validate(self, id: int) -> Result[Parameter, CustomException]:
        parameter_result = await self.repository.find_parameter_by_id(
            parameter_id=id, load_only_value=True
        )
        if parameter_result.is_failure:
            return self.not_found_failure

        return self.validate_instance(parameter_result.value)

    def validate_instance(
        self, parameter: Parameter
    ) -> Result[Parameter, CustomException]:
        if not parameter:
            return self.not_found_failure

        if parameter.category_id != self.param_category_id:
            return self.not_found_failure

        if not parameter.is_active:
            return self.disabled_failure

        return Success(parameter)
