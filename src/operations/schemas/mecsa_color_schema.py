from pydantic import Field, computed_field, field_validator
from slugify import slugify

from src.core.constants import PAGE_SIZE
from src.core.schemas import CustomBaseModel
from src.core.utils import is_active_status
from src.operations.constants import (
    DATOAUX_MAX_LENGTH,
    MAX_LENGTH_MECSA_COLOR_HEXADECIMAL,
    MAX_LENGTH_MECSA_COLOR_NAME,
    MAX_LENGTH_MECSA_COLOR_SKU,
)


class MecsaColorBase(CustomBaseModel):
    id: str
    name: str
    sku: str | None = None
    slug: str | None = None
    hexadecimal: str | None = None
    alias: str | None = Field(default=None, validation_alias="datoaux")
    is_active: bool

    class Config:
        from_attributes = True


class MecsaColorSchema(MecsaColorBase):
    @field_validator("is_active", mode="before")
    def convert_is_active(cls, value: str):
        return is_active_status(value)


class MecsaColorListSchema(CustomBaseModel):
    mecsa_colors: list[MecsaColorSchema]


class MecsaColorCreateSchema(CustomBaseModel):
    hexadecimal: str | None = Field(
        default=None, min_length=1, max_length=MAX_LENGTH_MECSA_COLOR_HEXADECIMAL
    )
    alias: str | None = Field(default=None, min_length=1, max_length=DATOAUX_MAX_LENGTH)


class MecsaColorUpdateSchema(MecsaColorCreateSchema):
    name: str = Field(
        default=None, min_length=1, max_length=MAX_LENGTH_MECSA_COLOR_NAME
    )


class MecsaColorFilterParams(CustomBaseModel):
    include_inactives: bool | None = Field(default=False)
    page: int | None = Field(default=1, ge=1)

    @computed_field
    def limit(self) -> int:
        return PAGE_SIZE

    @computed_field
    def offset(self) -> int:
        return (self.page - 1) * PAGE_SIZE
