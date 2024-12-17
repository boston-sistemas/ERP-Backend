from pydantic import AliasChoices, Field, computed_field, field_validator

from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH,
    MECSA_COLOR_ID_MAX_LENGTH,
    YARN_ID_MAX_LENGTH,
)
from src.security.schemas import ParameterValueSchema

from .inventory_item_schema import InventoryItemBase
from .mecsa_color_schema import MecsaColorSchema
from .yarn_schema import YarnSchema


class FabricBase(InventoryItemBase):
    density: float | None = Field(validation_alias=AliasChoices("field1"))
    width: float | None = Field(validation_alias=AliasChoices("field2"))
    # field3: str = Field(alias="colorId")
    # field4: str = Field(alias="typeFabricId")
    # field5: str = Field(alias="structurePattern")
    type_fabric: ParameterValueSchema | None = None
    color: MecsaColorSchema | None = Field(
        default=None, validation_alias=AliasChoices("yarn_color")
    )
    structure_pattern: str | None = Field(validation_alias=AliasChoices("field5"))

    @field_validator("density", "width", mode="before")
    @classmethod
    def convert_to_float(cls, value: str):
        if value and value.isdecimal():
            return float(value)

        return None


class FabricSchema(FabricBase):
    recipe: list["FabricRecipeItemSchema"] = []

    class Config:
        from_attributes = True


class FabricListSchema(CustomBaseModel):
    fabrics: list[FabricSchema]


class FabricRecipeItemSimpleSchema(CustomBaseModel):
    yarn_id: str = Field(max_length=YARN_ID_MAX_LENGTH)
    proportion: float = Field(gt=0.0)

    class Config:
        from_attributes = True


class FabricRecipeItemSchema(FabricRecipeItemSimpleSchema):
    yarn_id: str = Field(exclude=True)
    yarn: YarnSchema | None = None


class FabricCreateSchema(CustomBaseModel):
    fabric_type_id: int
    density: float = Field(examples=[120], le=1000)
    width: float = Field(examples=[90], le=1000)
    color_id: str | None = Field(default=None, max_length=MECSA_COLOR_ID_MAX_LENGTH)
    description: str = Field(max_length=INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH)
    structure_pattern: str  # TODO: reggex: LISO | 1x1 | 2x1 | 2x2

    recipe: list[FabricRecipeItemSimpleSchema]

    @field_validator("color_id", mode="after")
    @classmethod
    def set_color_id(cls, color_id: str | None) -> str:
        return "" if color_id is None else color_id

    @computed_field
    @property
    def fabric_type_id_(self) -> str | None:
        return str(self.fabric_type_id) if self.fabric_type_id is not None else ""
