from pydantic import Field, field_validator

from operations.constants import (
    MAX_LENGTH_MECSA_COLOR_HEXADECIMAL,
    MAX_LENGTH_MECSA_COLOR_NAME,
    MAX_LENGTH_MECSA_COLOR_SKU,
)
from src.core.schemas import CustomBaseModel


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
        return value == "A"


class MecsaColorListSchema(CustomBaseModel):
    mecsa_colors: list[MecsaColorSchema]


class MecsaColorCreateSchema(CustomBaseModel):
    name: str = Field(max_length=MAX_LENGTH_MECSA_COLOR_NAME)
    sku: str | None = Field(default=None, max_length=MAX_LENGTH_MECSA_COLOR_SKU)
    hexadecimal: str | None = Field(
        default=None, max_length=MAX_LENGTH_MECSA_COLOR_HEXADECIMAL
    )
