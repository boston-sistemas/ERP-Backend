from pydantic import (
    AliasChoices,
    Field,
    computed_field,
    field_validator,
)

from src.core.schemas import CustomBaseModel
from src.core.utils import to_safe_str
from src.operations.constants import (
    FIBER_ID_MAX_LENGTH,
    INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH,
    MECSA_COLOR_ID_MAX_LENGTH,
)
from src.security.schemas import ParameterValueSchema

from .fiber_schema import FiberSchema
from .inventory_item_schema import InventoryItemBase
from .mecsa_color_schema import MecsaColorSchema


class YarnOptions(CustomBaseModel):
    include_yarn_count: bool = False
    include_spinning_method: bool = False
    include_color: bool = False
    include_manufactured_in: bool = False
    include_recipe: bool = False
    include_fiber_instance: bool = False
    include_distinctions: bool = False
    include_distinction_instances: bool = False

    @staticmethod
    def all() -> "YarnOptions":
        return YarnOptions(
            include_yarn_count=True,
            include_spinning_method=True,
            include_color=True,
            include_manufactured_in=True,
            include_recipe=True,
            include_fiber_instance=True,
            include_distinctions=True,
            include_distinction_instances=True,
        )


class YarnBase(InventoryItemBase):
    # field1: str = Field(alias="yarnCount")
    # field2: str = Field(alias="spinningMethodId")
    # field3: str = Field(alias="colorId")
    # field4: str = Field(alias="manufacturedInId")
    distinction_ids: list[int] | None = Field(default=[], exclude=True)


class YarnSchema(YarnBase):
    yarn_count: ParameterValueSchema | None = None
    spinning_method: ParameterValueSchema | None = None
    manufactured_in: ParameterValueSchema | None = None
    color: MecsaColorSchema | None = Field(
        default=None, validation_alias=AliasChoices("yarn_color")
    )
    distinctions: list[ParameterValueSchema] = []
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
    fiber: FiberSchema | None = None


class YarnCreateSchema(CustomBaseModel):
    yarn_count_id: int
    spinning_method_id: int | None = None
    color_id: str | None = Field(default=None, max_length=MECSA_COLOR_ID_MAX_LENGTH)
    manufactured_in_id: int | None = None
    distinction_ids: list[int] = []
    description: str = Field(max_length=INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH)
    recipe: list[YarnRecipeItemSimpleSchema]

    @field_validator("color_id", mode="after")
    @classmethod
    def set_color_id(cls, color_id: str | None) -> str:
        return to_safe_str(color_id)

    @field_validator("distinction_ids", mode="after")
    @classmethod
    def set_unique_distinction_ids(cls, distinction_ids: list[int]) -> list[int]:
        return list(set(distinction_ids)) if distinction_ids else distinction_ids

    @computed_field
    @property
    def yarn_count_id_(self) -> str:
        return to_safe_str(self.yarn_count_id)

    @computed_field
    @property
    def spinning_method_id_(self) -> str:
        return to_safe_str(self.spinning_method_id)

    @computed_field
    @property
    def manufactured_in_id_(self) -> str:
        return to_safe_str(self.manufactured_in_id)


class YarnUpdateSchema(YarnCreateSchema):
    yarn_count_id: int = None
    description: str = Field(
        default=None, max_length=INVENTORY_ITEM_DESCRIPTION_MAX_LENGTH
    )

    recipe: list[YarnRecipeItemSimpleSchema] = None
