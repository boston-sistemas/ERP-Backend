from pydantic import Field
from pydantic_extra_types.country import CountryAlpha3

from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    FIBER_DENOMINATION_MAX_LENGTH,
    MECSA_COLOR_ID_MAX_LENGTH,
)
from src.security.schemas import ParameterValueSchema

from .mecsa_color_schema import MecsaColorSchema


class FiberBase(CustomBaseModel):
    id: str
    category_id: int
    denomination: str | None
    origin: str | None
    color_id: str | None

    class Config:
        from_attributes = True


class FiberSchema(FiberBase):
    pass


class FiberCompleteSchema(FiberSchema):
    category: ParameterValueSchema
    color: MecsaColorSchema | None = None


class FiberCompleteListSchema(CustomBaseModel):
    fibers: list[FiberCompleteSchema]


class FiberCreateSchema(CustomBaseModel):
    category_id: int
    denomination: str | None = Field(
        default=None, max_length=FIBER_DENOMINATION_MAX_LENGTH
    )
    origin: CountryAlpha3 | None = Field(default=None)
    color_id: str | None = Field(default=None, max_length=MECSA_COLOR_ID_MAX_LENGTH)
