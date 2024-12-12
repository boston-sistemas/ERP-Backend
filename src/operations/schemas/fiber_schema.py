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
    denomination: str | None
    origin: str | None
    is_active: bool

    class Config:
        from_attributes = True


class FiberSchema(FiberBase):
    pass


class FiberCompleteSchema(FiberSchema):
    category: ParameterValueSchema | None = None
    color: MecsaColorSchema | None = None


class FiberCompleteListSchema(CustomBaseModel):
    fibers: list[FiberCompleteSchema]


class FiberCreateSchema(CustomBaseModel):
    category_id: int
    denomination: str | None = Field(
        default=None, min_length=1, max_length=FIBER_DENOMINATION_MAX_LENGTH
    )
    origin: CountryAlpha3 | None = Field(default=None)
    color_id: str | None = Field(
        default=None, min_length=1, max_length=MECSA_COLOR_ID_MAX_LENGTH
    )


class FiberUpdateSchema(FiberCreateSchema):
    category_id: int | None = None
    denomination: str | None = Field(default=None, min_length=1)
    origin: CountryAlpha3 | None = Field(default=None)
    color_id: str | None = Field(default=None, min_length=1)
