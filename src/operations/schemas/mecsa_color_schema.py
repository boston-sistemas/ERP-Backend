from pydantic import Field, field_validator

from src.core.schemas import CustomBaseModel
from src.core.utils import is_active_status
from src.operations.constants import (
    MAX_LENGTH_MECSA_COLOR_HEXADECIMAL,
    MAX_LENGTH_MECSA_COLOR_NAME,
    MAX_LENGTH_MECSA_COLOR_SKU,
)


class MecsaColorBase(CustomBaseModel):
    id: str
    name: str
    sku: str | None = None
    hexadecimal: str | None = None
    is_active: bool

    class Config:
        from_attributes = True


class MecsaColorSchema(MecsaColorBase):
    @field_validator("is_active", mode="before")
    def convert_is_active(cls, value):
        return is_active_status(value)

    @field_validator("name", mode="after")
    def capitalize_name(cls, name: str):
        return name.capitalize()


class MecsaColorListSchema(CustomBaseModel):
    mecsa_colors: list[MecsaColorSchema]


class MecsaColorCreateSchema(CustomBaseModel):
    name: str = Field(min_length=1, max_length=MAX_LENGTH_MECSA_COLOR_NAME)
    sku: str | None = Field(
        default=None, min_length=1, max_length=MAX_LENGTH_MECSA_COLOR_SKU
    )
    hexadecimal: str | None = Field(
        default=None, min_length=1, max_length=MAX_LENGTH_MECSA_COLOR_HEXADECIMAL
    )

    @field_validator("name", "sku", mode="after")
    def to_uppercase(cls, value: str | None):
        return value.upper() if value else value
