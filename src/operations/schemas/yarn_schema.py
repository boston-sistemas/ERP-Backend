from enum import Enum
from typing import Self

from pydantic import (
    AliasChoices,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    FIBER_ID_MAX_LENGTH,
    INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH,
    INVENTORY_ITEM_FIELD1_MAX_LENGTH,
    MECSA_COLOR_ID_MAX_LENGTH,
)
from src.security.schemas import ParameterValueSchema

from .fiber_schema import FiberCompleteSchema
from .inventory_item_schema import InventoryItemBase
from .mecsa_color_schema import MecsaColorSchema


class YarnNumbering(str, Enum):
    ne = "Ne"
    dn = "Dn"


class YarnBase(InventoryItemBase):
    yarn_count: str | None = Field(
        default=None, validation_alias=AliasChoices("field1")
    )
    numbering_system: str | None = Field(
        default=None, validation_alias=AliasChoices("field2")
    )
    # field3: str = Field(alias="spinningMethodId")
    # field4: str = Field(alias="colorId")
    spinning_method: ParameterValueSchema | None = None
    color: MecsaColorSchema | None = Field(
        default=None, validation_alias=AliasChoices("yarn_color")
    )


class YarnSchema(YarnBase):
    recipe: list["YarnRecipeItemSchema"] = []

    class Config:
        from_attributes = True


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
    yarn_count: str = Field(
        default=None,
        pattern=r"^\d+(/\d+)?$",
        max_length=INVENTORY_ITEM_FIELD1_MAX_LENGTH,
        examples=["30/1", "28/1", "20"],
    )
    numbering_system: YarnNumbering = None
    spinning_method_id: int | None = None
    color_id: str | None = Field(default=None, max_length=MECSA_COLOR_ID_MAX_LENGTH)
    description: str = Field(
        default=None, max_length=INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH
    )

    recipe: list[YarnRecipeItemSimpleSchema] = None

    # spinning_method_id_: str | None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def validation(self) -> Self:
        if "color_id" in self.model_fields_set:
            self.color_id = "" if self.color_id is None else self.color_id

        self.__dict__["spinning_method_id_"] = (
            "" if self.spinning_method_id is None else str(self.spinning_method_id)
        )

        return self
