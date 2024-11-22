from pydantic import Field

from src.core.schemas import CustomBaseModel
from src.security.constants import (
    PARAMETER_CATEGORY_NAME_MAX_LENGTH,
)


class ParameterCategoryBase(CustomBaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ParameterCategorySchema(ParameterCategoryBase):
    pass


class ParameterCategoryListSchema(CustomBaseModel):
    parameter_categories: list[ParameterCategorySchema]


class ParameterCategoryCreateSchema(CustomBaseModel):
    name: str = Field(min_length=1, max_length=PARAMETER_CATEGORY_NAME_MAX_LENGTH)
