from pydantic import Field
from pydantic_extra_types.country import CountryAlpha3

from src.core.schemas import CustomBaseModel, ItemIsUpdatableSchema
from src.operations.constants import (
    MECSA_COLOR_ID_MAX_LENGTH,
)
from src.security.schemas import ParameterValueSchema

from .mecsa_color_schema import MecsaColorSchema


class FiberOptions(CustomBaseModel):
    include_category: bool = False
    include_denomination: bool = False
    include_color: bool = False

    @staticmethod
    def all() -> "FiberOptions":
        return FiberOptions(
            include_category=True, include_denomination=True, include_color=True
        )


class FiberBase(CustomBaseModel):
    id: str
    origin: str | None
    is_active: bool

    class Config:
        from_attributes = True


class FiberSimpleSchema(FiberBase):
    pass


class FiberSchema(FiberSimpleSchema):
    category: ParameterValueSchema | None = None
    denomination: ParameterValueSchema | None = None
    color: MecsaColorSchema | None = None


class FiberExtendedSchema(FiberSchema):
    update_check: ItemIsUpdatableSchema = Field(default=None)


class FiberListSchema(CustomBaseModel):
    fibers: list[FiberSchema]


class FiberExtendedListSchema(CustomBaseModel):
    fibers: list[FiberExtendedSchema]


class FiberCreateSchema(CustomBaseModel):
    category_id: int
    denomination_id: int | None = Field(default=None)
    origin: CountryAlpha3 | None = Field(default=None)
    color_id: str | None = Field(
        default=None, min_length=1, max_length=MECSA_COLOR_ID_MAX_LENGTH
    )


class FiberUpdateSchema(FiberCreateSchema):
    category_id: int = None
