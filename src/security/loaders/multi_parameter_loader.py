from src.security.models import Parameter

from .abstract_loader import AbstractParameterLoader


class MultiParameterLoader(AbstractParameterLoader):
    ids: list[int]

    def __init_subclass__(cls, ids: list[int] = None, **kwargs):
        if ids is None:
            raise TypeError(f"{cls.__name__} requires 'ids' to be defined.")
        cls.ids = ids
        super().__init_subclass__(**kwargs)

    async def get(self, include_inactives: bool = False) -> list[Parameter]:
        parameters = await self.repository.find_parameters(
            filter=Parameter.id.in_(self.ids),
            load_only_value=True,
            include_inactives=include_inactives,
        )
        return parameters

    async def get_and_mapping(
        self, include_inactives: bool = False
    ) -> dict[int, Parameter]:
        values = await self.get(include_inactives=include_inactives)
        return {value.id: value for value in values}
