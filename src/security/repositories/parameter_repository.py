from typing import Sequence, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.security.models import Parameter


class ParameterRepository(BaseRepository[Parameter]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Parameter, db, flush)

    @staticmethod
    def include_category() -> Load:
        return joinedload(Parameter.category)

    @staticmethod
    def load_only_value() -> Load:
        return load_only(
            Parameter.value, Parameter.category_id, Parameter.is_active, raiseload=True
        )

    def get_load_options(
        self, include_category: bool = False, load_only_value: bool = False
    ) -> list[Load]:
        options: list[Load] = []

        if include_category:
            options.append(self.include_category())

        if load_only_value:
            options.append(self.load_only_value())

        return options

    async def find_parameter_by_id(
        self,
        parameter_id: int,
        include_category: bool = False,
        load_only_value: bool = False,
        **kwargs,
    ) -> Parameter | None:
        options = self.get_load_options(
            include_category=include_category, load_only_value=load_only_value
        )
        parameter = await self.find_by_id(parameter_id, options=options, **kwargs)

        return parameter

    async def find_parameters(
        self,
        filter: BinaryExpression = None,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
        include_inactives: bool = True,
        include_category: bool = False,
        load_only_value: bool = False,
    ) -> list[Parameter]:
        if not include_inactives:
            filter = (
                filter & (Parameter.is_active == bool(True))
                if filter is not None
                else Parameter.is_active == bool(True)
            )
        options = self.get_load_options(
            include_category=include_category, load_only_value=load_only_value
        )
        parameters = await self.find_all(
            filter=filter, options=options, order_by=order_by
        )

        return parameters
