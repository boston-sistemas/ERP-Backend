from pydantic import Field, computed_field

from typing import Any

from datetime import date

from src.core.schemas import CustomBaseModel

from .yarn_purchase_entry_detalle_heavy_schema import (
    YarnPurchaseEntryDetalleHeavySimpleSchema
)

class YarnPurchaseEntryDetalleBase(CustomBaseModel):
    item_number: int | None
    yarn_code: str | None = Field(alias="product_code")
    quantity: float | None
    mecsa_weight: float | None
    status_flag: str | None

    class Config:
        from_attributes = True

class YarnPurchaseEntryDetalleSimpleSchema(YarnPurchaseEntryDetalleBase):
    detalle_aux: Any = Field(default=None, exclude=True)
    detalle_heavy: list[YarnPurchaseEntryDetalleHeavySimpleSchema]

    @computed_field
    @property
    def net_weight(self) -> float | None:
        if self.detalle_aux and hasattr(self.detalle_aux, "net_weight"):
            return self.detalle_aux.net_weight
        return None

    @computed_field
    @property
    def gross_weight(self) -> float | None:
        if self.detalle_aux and hasattr(self.detalle_aux, "gross_weight"):
            return self.detalle_aux.gross_weight
        return None

    @computed_field
    @property
    def cone_count(self) -> int | None:
        if self.detalle_aux and hasattr(self.detalle_aux, "cone_count"):
            return self.detalle_aux.cone_count
        return None

    @computed_field
    @property
    def package_count(self) -> int | None:
        if self.detalle_aux and hasattr(self.detalle_aux, "package_count"):
            return self.detalle_aux.package_count
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
        if self.detalle_aux and hasattr(self.detalle_aux, "reference_code"):
            return self.detalle_aux.reference_code
        return None

class YarnPurchaseEntryDetalleListSchema(CustomBaseModel):
    yarn_purchase_entry_detalles: list[YarnPurchaseEntryDetalleBase] = []
