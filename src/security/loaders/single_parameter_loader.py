from src.security.models import Parameter

from .abstract_loader import AbstractParameterLoader


class SingleParameterLoader(AbstractParameterLoader):
    id: int

    def __init_subclass__(cls, id: int = None, **kwargs):
        if id is None:
            raise TypeError(f"{cls.__name__} requires 'id' to be defined.")
        cls.id = id
        super().__init_subclass__(**kwargs)

    async def get(
        self,
    ) -> Parameter:
        parameter = await self.repository.find_parameter_by_id(
            parameter_id=self.id, load_only_value=True
        )
        if parameter:
            return parameter

        raise self.not_found_failure
