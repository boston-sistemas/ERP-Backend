from enum import Enum
from typing import Self

from pydantic import Field, computed_field, field_validator, model_validator

from src.core.schemas import CustomBaseModel
from src.core.utils import is_active_status
from src.operations.constants import (
    FIBER_ID_MAX_LENGTH,
    INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH,
    INVENTORY_ITEM_FIELD1_MAX_LENGTH,
    MECSA_COLOR_ID_MAX_LENGTH,
)
from src.security.schemas import ParameterValueSchema

from .fiber_schema import FiberCompleteSchema
from .mecsa_color_schema import MecsaColorSchema


class YarnNumbering(str, Enum):
    ne = "Ne"
    dn = "Dn"


class YarnBase(CustomBaseModel):
    id: str
    inventory_unit_code: str | None
    purchase_unit_code: str | None
    description: str | None
    purchase_description: str | None
    barcode: int | None
    field1: str | None = Field(alias="yarnCount", exclude=True)
    field2: str | None = Field(alias="numberingSystem", exclude=True)
    # field3: str = Field(alias="spinningMethodId")
    # field4: str = Field(alias="colorId")
    is_active: bool

    spinning_method: ParameterValueSchema | None = None
    yarn_color: MecsaColorSchema | None = Field(default=None, alias="color")

    @computed_field
    @property
    def yarn_count(self) -> str | None:
        return self.field1 if self.field1 else None

    @computed_field
    @property
    def numbering_system(self) -> str | None:
        return self.field2 if self.field2 else None

    @field_validator("is_active", mode="before")
    def convert_is_active(cls, value):
        return is_active_status(value)

    class Config:
        from_attributes = True


class YarnSchema(YarnBase):
    recipe: list["YarnRecipeItemSchema"] = []


class YarnListSchema(CustomBaseModel):
    yarns: list[YarnSchema]


class YarnRecipeItemSimpleSchema(CustomBaseModel):
    fiber_id: str = Field(max_length=FIBER_ID_MAX_LENGTH)
    proportion: float = Field(gt=0.0)

    class Config:
        from_attributes = True


class YarnRecipeItemSchema(YarnRecipeItemSimpleSchema):
    fiber_id: str = Field(exclude=True)
    fiber: FiberCompleteSchema | None = None


class YarnCreateSchema(CustomBaseModel):
    yarn_count: str = Field(
        pattern=r"^\d+(/\d+)?$",
        max_length=INVENTORY_ITEM_FIELD1_MAX_LENGTH,
        examples=["30/1", "28/1", "20"],
    )
    numbering_system: YarnNumbering = YarnNumbering.ne
    spinning_method_id: int | None = None
    color_id: str | None = Field(default=None, max_length=MECSA_COLOR_ID_MAX_LENGTH)
    description: str = Field(max_length=INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH)

    recipe: list[YarnRecipeItemSimpleSchema]

    @field_validator("color_id", mode="after")
    @classmethod
    def set_color_id(cls, color_id: str | None) -> str:
        return "" if color_id is None else color_id

    @computed_field
    @property
    def spinning_method_id_(self) -> str | None:
        return (
            str(self.spinning_method_id) if self.spinning_method_id is not None else ""
        )


class YarnUpdateSchema(CustomBaseModel):
    yarn_count: str | None = Field(
        default=None,
        pattern=r"^\d+(/\d+)?$",
        max_length=INVENTORY_ITEM_FIELD1_MAX_LENGTH,
        examples=["30/1", "28/1", "20"],
    )
    numbering_system: YarnNumbering | None = None
    spinning_method_id: int | None = None
    color_id: str | None = Field(default=None, max_length=MECSA_COLOR_ID_MAX_LENGTH)
    description: str | None = Field(
        default=None, max_length=INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH
    )

    recipe: list[YarnRecipeItemSimpleSchema] | None = None

    # spinning_method_id_: str | None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def validation(self) -> Self:
        if "color_id" in self.model_fields_set:
            self.color_id = "" if self.color_id is None else self.color_id

        self.__dict__["spinning_method_id_"] = (
            "" if self.spinning_method_id is None else str(self.spinning_method_id)
        )

        return self
