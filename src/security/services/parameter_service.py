from datetime import datetime
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import (
    PARAMETER_CATEGORY_NOT_FOUND_WHEN_CREATING_FAILURE,
    PARAMETER_NOT_FOUND_FAILURE,
    PARAMETER_VALUE_CONVERSION_FAILURE,
    PARAMETER_VALUE_CONVERSION_TO_BOOLEAN_FAILURE,
    PARAMETER_VALUE_CONVERSION_TO_DATE_FAILURE,
    PARAMETER_VALUE_CONVERSION_TO_DATETIME_FAILURE,
    PARAMETER_VALUE_CONVERSION_TO_FLOAT_FAILURE,
    PARAMETER_VALUE_CONVERSION_TO_INT_FAILURE,
)
from src.security.loaders import MultiParameterLoaderByCategory
from src.security.models import Parameter
from src.security.repositories import ParameterRepository
from src.security.schemas import DataType, ParameterCreateSchema

from .parameter_category_service import ParameterCategoryService


class ParameterService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = ParameterRepository(db=db)
        self.parameter_category_service = ParameterCategoryService(db=db)

    def _validate_value(
        self, data_type: DataType, value: str
    ) -> Result[None, CustomException]:
        def _func(
            validator: Callable, failure: Callable, value: str
        ) -> Result[None, CustomException]:
            try:
                validator(value)
                return Success(None)
            except Exception:
                if failure is not None:
                    return failure(value)
                return PARAMETER_VALUE_CONVERSION_FAILURE(value)

        VALIDATORS = {
            DataType.STRING: (lambda value: True, None),
            DataType.INTEGER: (
                lambda value: int(value),
                PARAMETER_VALUE_CONVERSION_TO_INT_FAILURE,
            ),
            DataType.FLOAT: (
                lambda value: float(value),
                PARAMETER_VALUE_CONVERSION_TO_FLOAT_FAILURE,
            ),
            DataType.BOOLEAN: (
                lambda value: True if value.lower() in {"true", "false"} else 1 / 0,
                PARAMETER_VALUE_CONVERSION_TO_BOOLEAN_FAILURE,
            ),
            DataType.DATE: (
                lambda value: datetime.strptime(value, "%d/%m/%Y"),
                PARAMETER_VALUE_CONVERSION_TO_DATE_FAILURE,
            ),
            DataType.DATETIME: (
                lambda value: datetime.strptime(value, "%d/%m/%Y %H:%M:%S"),
                PARAMETER_VALUE_CONVERSION_TO_DATETIME_FAILURE,
            ),
            DataType.LIST_STRING: (lambda value: True, None),
        }

        validator, failure = VALIDATORS.get(data_type, None)
        return _func(validator, failure, value)

    async def _validate_parameter_data(
        self, value: str, data_type: DataType, category_id: int | None = None
    ) -> Result[None, CustomException]:
        if category_id is not None:
            result = await self.parameter_category_service.read_parameter_category(
                parameter_category_id=category_id
            )
            if result.is_failure:
                return PARAMETER_CATEGORY_NOT_FOUND_WHEN_CREATING_FAILURE

        value_validation_result = self._validate_value(data_type=data_type, value=value)
        return value_validation_result

    async def read_parameter(
        self,
        parameter_id: int,
        include_category: bool = False,
        load_only_value: bool = False,
    ) -> Result[Parameter, CustomException]:
        parameter = await self.repository.find_parameter_by_id(
            parameter_id,
            include_category=include_category,
            load_only_value=load_only_value,
        )
        if parameter is not None:
            return Success(parameter)

        return PARAMETER_NOT_FOUND_FAILURE

    async def read_parameters(
        self, include_category: bool = False, load_only_value: bool = False
    ) -> Result[list[Parameter], CustomException]:
        parameters = await self.repository.find_parameters(
            order_by=Parameter.id.asc(),
            include_category=include_category,
            load_only_value=load_only_value,
        )

        return Success(parameters)

    async def create_parameter(
        self, form: ParameterCreateSchema
    ) -> Result[Parameter, CustomException]:
        validation_result = await self._validate_parameter_data(
            value=form.value, data_type=form.data_type, category_id=form.category_id
        )

        if validation_result.is_failure:
            return validation_result

        parameter = Parameter(**form.model_dump())
        await self.repository.save(parameter)

        return Success(parameter)

    async def read_parameters_by_category(
        self,
        parameter_category_id: int,
        include_category: bool = False,
        load_only_value: bool = False,
        include_inactives: bool = True,
    ) -> Result[list[Parameter], CustomException]:
        parameters = await self.repository.find_parameters(
            filter=Parameter.category_id == parameter_category_id,
            order_by=Parameter.id.asc(),
            include_inactives=include_inactives,
            include_category=include_category,
            load_only_value=load_only_value,
        )

        return Success(parameters)

    async def read_parameters_by_ids(
        self,
        parameter_ids: list[int],
        include_category: bool = False,
        load_only_value: bool = False,
        include_inactives: bool = True,
    ) -> Result[list[Parameter], CustomException]:
        if not parameter_ids:
            return Success([])

        if len(parameter_ids) == 1:
            id = parameter_ids[0]
            result = await self.read_parameter(
                parameter_id=id,
                include_category=include_category,
                load_only_value=load_only_value,
            )
            if result.is_success and (include_inactives or result.value.is_active):
                return Success([result.value])

            return Success([])

        parameters = await self.repository.find_parameters(
            filter=Parameter.id.in_(parameter_ids),
            include_inactives=include_inactives,
            include_category=include_category,
            load_only_value=load_only_value,
        )
        return Success(parameters)

    async def map_parameters_by_ids(
        self,
        parameter_ids: list[int],
        include_category: bool = False,
        load_only_value: bool = False,
    ) -> Result[dict[int, Parameter], CustomException]:
        parameters = (
            await self.read_parameters_by_ids(
                parameter_ids=parameter_ids,
                include_category=include_category,
                load_only_value=load_only_value,
            )
        ).value

        return Success({parameter.id: parameter for parameter in parameters})

    async def validate_parameters(
        self,
        parameter_id_validator_pairs: list[
            tuple[int | None, MultiParameterLoaderByCategory]
        ],
    ) -> Result[None, CustomException]:
        validator_mapping = {
            parameter_id: validator
            for parameter_id, validator in parameter_id_validator_pairs
            if parameter_id is not None
        }
        mapping = (
            await self.map_parameters_by_ids(
                parameter_ids=list(validator_mapping.keys()), load_only_value=True
            )
        ).value
        for parameter_id, validator in validator_mapping.items():
            validation = validator.validate_instance(mapping.get(parameter_id))
            if validation.is_failure:
                return validation

        return Success(None)
