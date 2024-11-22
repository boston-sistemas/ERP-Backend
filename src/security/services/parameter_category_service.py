from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.security.failures import (
    PARAMETER_CATEGORY_NAME_ALREADY_EXISTS,
    PARAMETER_CATEGORY_NOT_FOUND_FAILURE,
)
from src.security.models import ParameterCategory
from src.security.schemas import ParameterCategoryCreateSchema


class ParameterCategoryService:
    def __init__(self, db: AsyncSession):
        self.repository = BaseRepository[ParameterCategory](
            model=ParameterCategory, db=db
        )

    async def _validate_parameter_category_data(self, name: str):
        name_exists = await self.repository.find(ParameterCategory.name == name)

        if name_exists is not None:
            return PARAMETER_CATEGORY_NAME_ALREADY_EXISTS(name)

        return Success(None)

    async def read_parameter_category(
        self, parameter_category_id: int
    ) -> Result[ParameterCategory, CustomException]:
        category = await self.repository.find_by_id(parameter_category_id)
        if category is not None:
            return Success(category)

        return PARAMETER_CATEGORY_NOT_FOUND_FAILURE

    async def read_parameter_categories(
        self,
    ) -> Result[list[ParameterCategory], CustomException]:
        categories = await self.repository.find_all()

        return Success(categories)

    async def create_parameter_category(
        self, form: ParameterCategoryCreateSchema
    ) -> Result[ParameterCategory, CustomException]:
        validation_result = await self._validate_parameter_category_data(name=form.name)

        if validation_result.is_failure:
            return validation_result

        parameter_category = ParameterCategory(**form.model_dump())
        await self.repository.save(parameter_category)

        return Success(parameter_category)
