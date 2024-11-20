from pydantic import Field

from src.core.schemas import CustomBaseModel
from src.security.constants import (
    PARAMETER_DESCRIPTION_MAX_LENGTH,
    PARAMETER_VALUE_MAX_LENGTH,
)

from .parameter_category_schema import ParameterCategorySchema
from .parameter_public_schema import DataType


class ParameterBase(CustomBaseModel):
    id: int
    category_id: int | None = None
    description: str | None = None
    value: str
    data_type: str
    is_active: bool

    class Config:
        from_attributes = True


class ParameterSchema(ParameterBase):
    pass


class ParameterWithCategorySchema(ParameterSchema):
    category: ParameterCategorySchema | None = None


class ParameterWithCategoryListSchema(CustomBaseModel):
    parameters: list[ParameterWithCategorySchema]


class ParameterCreateSchema(CustomBaseModel):
    category_id: int | None = None
    description: str | None = Field(
        default=None, max_length=PARAMETER_DESCRIPTION_MAX_LENGTH
    )
    data_type: DataType
    value: str = Field(min_length=1, max_length=PARAMETER_VALUE_MAX_LENGTH)
