from datetime import date
from typing import Any

from pydantic import AliasChoices, Field, computed_field

from src.core.schemas import CustomBaseModel
from src.operations.constants import PRODUCT_CODE_MAX_LENGTH

from .yarn_purchase_entry_detalle_heavy_schema import (
    YarnPurchaseEntryDetalleHeavyCreateSchema,
    YarnPurchaseEntryDetalleHeavySimpleSchema,
)


class YarnPurchaseEntryDetalleBase(CustomBaseModel):
    item_number: int | None
    yarn_id: str | None = Field(
        validation_alias=AliasChoices("product_code", "yarn_id"),
    )
    mecsa_weight: float | None
    status_flag: str | None

    class Config:
        from_attributes = True


class YarnPurchaseEntryDetalleSimpleSchema(YarnPurchaseEntryDetalleBase):
    detail_aux: Any = Field(default=None, exclude=True)
    detail_heavy: list[YarnPurchaseEntryDetalleHeavySimpleSchema]

    @computed_field
    @property
    def guide_net_weight(self) -> float | None:
        if self.detail_aux and hasattr(self.detail_aux, "net_weight"):
            return self.detail_aux.net_weight
        return None

    @computed_field
    @property
    def guide_gross_weight(self) -> float | None:
        if self.detail_aux and hasattr(self.detail_aux, "gross_weight"):
            return self.detail_aux.gross_weight
        return None

    @computed_field
    @property
    def guide_cone_count(self) -> int | None:
        if self.detail_aux and hasattr(self.detail_aux, "cone_count"):
            return self.detail_aux.cone_count
        return None

    @computed_field
    @property
    def guide_package_count(self) -> int | None:
        if self.detail_aux and hasattr(self.detail_aux, "package_count"):
            return self.detail_aux.package_count
        return None


class YarnPurchaseEntryDetalleSchema(YarnPurchaseEntryDetalleSimpleSchema):
    creation_date: date | None
    creation_time: str | None
    precto: float | None
    impcto: float | None
    impmn1: float | None
    impmn2: float | None
    ctomn1: float | None
    ctomn2: float | None

    @computed_field
    @property
    def reference_code(self) -> str | None:
        if self.detail_aux and hasattr(self.detail_aux, "reference_code"):
            return self.detail_aux.reference_code
        return None


class YarnPurchaseEntryDetalleListSchema(CustomBaseModel):
    yarn_purchase_entry_detalles: list[YarnPurchaseEntryDetalleBase] = []


class YarnPurchaseEntryDetalleCreateSchema(CustomBaseModel):
    item_number: int | None = Field(default=0, ge=1)
    yarn_id: str = Field(max_length=PRODUCT_CODE_MAX_LENGTH)
    guide_net_weight: float = Field(gt=0.0)
    guide_gross_weight: float = Field(gt=0.0)
    guide_cone_count: int = Field(gt=0)
    guide_package_count: int = Field(gt=0)

    detail_heavy: list[YarnPurchaseEntryDetalleHeavyCreateSchema] = Field(default=[])
