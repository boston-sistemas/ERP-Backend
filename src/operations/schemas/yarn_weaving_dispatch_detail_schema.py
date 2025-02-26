from datetime import date
from typing import Any

from pydantic import AliasChoices, Field, computed_field

from src.core.schemas import CustomBaseModel
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import PRODUCT_ID_MAX_LENGTH

from .yarn_purchase_entry_detail_heavy_schema import (
    YarnPurchaseEntryDetailHeavySchema,
)


class YarnWeavingDispatchDetailBase(CustomBaseModel):
    item_number: int | None = None
    entry_number: str | None = Field(
        None,
        validation_alias=AliasChoices("reference_number"),
    )
    entry_group_number: int | None = None
    entry_item_number: int | None = None
    entry_period: int | None = None
    creation_date: date | None
    creation_time: str | None

    class Config:
        from_attributes = True


class YarnWeavingDispatchDetailWithEntryYarnHeavySchema(YarnWeavingDispatchDetailBase):
    yarn_purchase_entry: Any | None = Field(
        None,
        exclude=True,
        validation_alias=AliasChoices("movement_ingress", "yarn_purchase_entry"),
    )

    detail_aux: Any = Field(default=None, exclude=True)
    yarn_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("product_code1"),
    )
    fabric_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("product_code2"),
    )

    @computed_field
    @property
    def net_weight(self) -> float | None:
        if self.detail_aux and hasattr(self.detail_aux, "mecsa_weight"):
            return self.detail_aux.mecsa_weight
        return None

    @computed_field
    @property
    def gross_weight(self) -> float | None:
        if self.detail_aux and hasattr(self.detail_aux, "guide_net_weight"):
            return self.detail_aux.guide_net_weight
        return None

    @computed_field
    @property
    def cone_count(self) -> int | None:
        if self.detail_aux and hasattr(self.detail_aux, "guide_cone_count"):
            return self.detail_aux.guide_cone_count
        return None

    @computed_field
    @property
    def package_count(self) -> int | None:
        if self.detail_aux and hasattr(self.detail_aux, "guide_package_count"):
            return self.detail_aux.guide_package_count
        return None

    # @computed_field
    # @property
    # def yarn_id(self) -> str | None:
    #     if self.yarn_purchase_entry and hasattr(
    #         self.yarn_purchase_entry, "movement_detail"
    #     ):
    #         return self.yarn_purchase_entry.yarn_id
    #     return None


class YarnWeavingDispatchDetailCreateSchema(CustomBaseModel):
    item_number: int | None = Field(default=None, ge=1)
    entry_number: str
    entry_group_number: int
    entry_item_number: int
    entry_period: int = Field(ge=0)
    cone_count: int = Field(..., ge=1)
    package_count: int = Field(..., ge=0)
    net_weight: float = Field(..., gt=0)
    gross_weight: float = Field(..., gt=0)
    fabric_id: str | None = Field(max_length=PRODUCT_ID_MAX_LENGTH)

    _yarn_purchase_entry_heavy: YarnPurchaseEntryDetailHeavySchema | None = None


class YarnWeavingDispatchDetailUpdateSchema(YarnWeavingDispatchDetailCreateSchema):
    item_number: int = Field(ge=1)
