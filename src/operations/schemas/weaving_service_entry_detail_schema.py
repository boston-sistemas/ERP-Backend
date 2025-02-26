from typing import Any

from pydantic import Field, computed_field, model_validator

from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    COLOR_ID_MAX_LENGTH,
    FABRIC_ID_MAX_LENGTH,
    FABRIC_TYPE_MAX_LENGTH,
    SERVICE_ORDER_ID_MAX_LENGTH,
    SUPPLIER_CODE_MAX_LENGTH,
    SUPPLIER_COLOR_ID_MAX_LENGTH,
)
from src.operations.models import ServiceOrderSupplyDetail

from .card_operation_schema import (
    CardOperationSchema,
    CardOperationUpdateSchema,
)
from .fabric_schema import (
    FabricSchema,
)


class WeavingServiceEntryDetailBase(CustomBaseModel):
    item_number: int | None
    fabrid_id: str | None = Field(
        validation_alias="product_code1",
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

    detail_card: list[CardOperationSchema] | None = []

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


class WeavingServiceEntryDetailCreateSchema(CustomBaseModel):
    item_number: int | None = Field(default=None, ge=1)
    guide_net_weight: float = Field(gt=0.0)
    roll_count: int = Field(gt=0)
    service_order_id: str = Field(max_length=SERVICE_ORDER_ID_MAX_LENGTH)
    service_order_ids: list[str] | None = Field(default=[])
    fabric_id: str = Field(max_length=FABRIC_ID_MAX_LENGTH)
    fabric_type: str = Field(default="A", max_length=FABRIC_TYPE_MAX_LENGTH)
    tint_color_id: str | None = Field(default=None, max_length=COLOR_ID_MAX_LENGTH)
    tint_supplier_id: str | None = Field(
        default=None, max_length=SUPPLIER_CODE_MAX_LENGTH
    )
    tint_supplier_color_id: str | None = Field(
        default=None, max_length=SUPPLIER_COLOR_ID_MAX_LENGTH
    )
    generate_cards: bool | None = Field(default=False)

    _fabric: FabricSchema | None = None
    _service_orders_supply_stock: list[ServiceOrderSupplyDetail] | None = None

    # Posible forma de encapsular la validación de los campos
    @model_validator(mode="after")
    def validate_tint_fields(self):
        if bool(self.tint_supplier_id) ^ bool(self.tint_supplier_color_id):
            raise ValueError(
                "El código de proveedor y el código de color del proveedor deben ser mandados."
            )
        return self


class WeavingServiceEntryDetailUpdateSchema(WeavingServiceEntryDetailCreateSchema):
    detail_card: list[CardOperationUpdateSchema] | None = []
