from decimal import Decimal

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
    fabric_type: ParameterValueSchema | None = None
    color: MecsaColorSchema | None = Field(
        default=None, validation_alias=AliasChoices("fabric_color")
    )
    structure_pattern: str | None = Field(validation_alias=AliasChoices("field5"))

    @field_validator("density", "width", mode="before")
    @classmethod
    def convert_to_float(cls, value: str):
        try:
            return float(Decimal(value)) if value else None
        except Exception:
            return None


class FabricSchema(FabricBase):
    recipe: list["FabricRecipeItemSchema"] = Field(
        default=[], validation_alias=AliasChoices("fabric_recipe")
    )

    supplier_yarn_ids: list[str] = Field(default=[], exclude=True)

    class Config:
        from_attributes = True


class FabricListSchema(CustomBaseModel):
    fabrics: list[FabricSchema]


class FabricRecipeItemSimpleSchema(CustomBaseModel):
    yarn_id: str = Field(max_length=YARN_ID_MAX_LENGTH)
    proportion: float = Field(gt=0.0)
    num_plies: int = Field(default=1, ge=1, le=100)
    galgue: float = Field(default=0.0, ge=0.0)
    diameter: float = Field(default=0.0, ge=0.0)
    stitch_length: float = Field(default=0.0, ge=0.0)

    class Config:
        from_attributes = True


class FabricRecipeItemSchema(FabricRecipeItemSimpleSchema):
    yarn_id: str = Field(exclude=True)
    yarn: YarnSchema | None = None


class FabricCreateSchema(CustomBaseModel):
    fabric_type_id: int
    density: float = Field(examples=[135], le=1000)
    width: float = Field(examples=[90], le=1000)
    color_id: str | None = Field(default=None, max_length=MECSA_COLOR_ID_MAX_LENGTH)
    structure_pattern: str | None = Field(default="LISO", pattern=r"^(LISO|\d+x\d+)$")
    description: str = Field(max_length=INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH)

    recipe: list[FabricRecipeItemSimpleSchema]

    @field_validator("color_id", mode="after")
    @classmethod
    def set_color_id(cls, color_id: str | None) -> str:
        return "" if color_id is None else color_id

    @field_validator("structure_pattern", mode="after")
    @classmethod
    def set_structure_pattern(cls, structure_pattern: str | None) -> str:
        return "" if structure_pattern is None else structure_pattern

    @computed_field
    @property
    def fabric_type_id_(self) -> str | None:
        return str(self.fabric_type_id) if self.fabric_type_id is not None else ""

    @computed_field
    @property
    def width_(self) -> str | None:
        return str(self.width)


class FabricUpdateSchema(CustomBaseModel):
    fabric_type_id: int = Field(default=None)
    density: float = Field(default=None, examples=[135], le=1000)
    width: float = Field(default=None, examples=[90], le=1000)
    color_id: str | None = Field(default=None)
    structure_pattern: str | None = Field(default=None, pattern=r"^(LISO|\d+x\d+)$")
    description: str = Field(
        default=None, max_length=INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH
    )

    recipe: list[FabricRecipeItemSimpleSchema] = None
