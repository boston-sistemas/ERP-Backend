from datetime import date
from typing import Any

from pydantic import AliasChoices, Field, computed_field, model_validator

from src.core.schemas import CustomBaseModel
from src.operations.constants import PRODUCT_CODE_MAX_LENGTH

from .card_operation_schema import (
    CardOperationSchema,
)

class WeavingServiceEntryDetailBase(CustomBaseModel):

    item_number: int | None
    fabrid_id: str | None = Field(
        validation_alias="product_code",
    )
    mecsa_weight: float | None
    status_flag: str | None
    service_order_id: str | None = Field(
        validation_alias="reference_number",
    )

    class Config:
        from_attributes = True

class WeavingServiceEntrySimpleSchema(WeavingServiceEntryDetailBase):

    pass

class WeavingServiceEntryDetailSchema(WeavingServiceEntrySimpleSchema):
    detail_fabric: Any = Field(default=None, exclude=True)

    @computed_field
    @property
    def guide_net_weight(self) -> float | None:
        if self.detail_fabric and hasattr(self.detail_fabric, "guide_net_weight"):
            return self.detail_fabric.guide_net_weight
        return None

    @computed_field
    @property
    def roll_count(self) -> int | None:
        if self.detail_fabric and hasattr(self.detail_fabric, "roll_count"):
            return self.detail_fabric.roll_count
        return None

    @computed_field
    @property
    def fabric_type(self) -> str | None:
        if self.detail_fabric and hasattr(self.detail_fabric, "fabric_type"):
            return self.detail_fabric.fabric_type
        return None

    @computed_field
    @property
    def tint_color_id(self) -> str | None:
        if self.detail_fabric and hasattr(self.detail_fabric, "tint_color_id"):
            return self.detail_fabric.tint_color_id
        return None

    @computed_field
    @property
    def tint_supplier_id(self) -> str | None:
        if self.detail_fabric and hasattr(self.detail_fabric, "tint_supplier_id"):
            return self.detail_fabric.tint_supplier_id
        return None

    @computed_field
    @property
    def tint_supplier_color_id(self) -> str | None:
        if self.detail_fabric and hasattr(self.detail_fabric, "tint_supplier_color_id"):
            return self.detail_fabric.tint_supplier_color_id
        return None

    detail_card: list[CardOperationSchema] | None = []


class WeavingServiceEntryDetailCreateSchema(CustomBaseModel):
    pass

class WeavingServiceEntryDetailUpdateSchema(CustomBaseModel):
    pass
