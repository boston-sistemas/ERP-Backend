from pydantic import Field, model_validator

from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    CARD_ID_MAX_LENGTH,
    CARD_TYPE_MAX_LENGTH,
    COLOR_ID_MAX_LENGTH,
    FABRIC_ID_MAX_LENGTH,
    SUPPLIER_CODE_MAX_LENGTH,
)


class CardOperationBase(CustomBaseModel):
    id: str | None = None
    fabric_id: str | None
    net_weight: float | None
    tint_supplier_id: str | None
    tint_color_id: str | None
    yarn_supplier_id: str | None
    card_type: str | None
    product_id: str | None
    status_flag: str | None = None

    class Config:
        from_attributes = True


class CardOperationSimpleSchema(CardOperationBase):
    pass


class CardOperationSchema(CardOperationSimpleSchema):
    id: str | None = None
    exit_number: str | None = None
    service_order_id: str | None = None
    supplier_weaving_tej: str | None = None

    _supplier_weaving_tej_initials: str | None = None
    _supplier_tint_initials: str | None = None
    _supplier_yarn_initials: list[str] | None = []

    suppliers_yarn: list[str] | None = []
    service_orders: list[str] | None = []

    @model_validator(mode="after")
    def set_suppliers_yarn(self):
        self.suppliers_yarn = self.yarn_supplier_id.split(",")
        return self

    @model_validator(mode="after")
    def set_service_orders(self):
        self.service_orders = self.service_order_id.split(",")
        return self


class CardOperationListSchema(CustomBaseModel):
    card_operations: list[CardOperationSchema]


class CardOperationCreateSchema(CustomBaseModel):
    fabric_id: str = Field(max_length=FABRIC_ID_MAX_LENGTH)
    net_weight: float
    tint_supplier_id: str = Field(max_length=SUPPLIER_CODE_MAX_LENGTH)
    tint_color_id: str = Field(max_length=COLOR_ID_MAX_LENGTH)
    yarn_supplier_id: str = Field(max_length=SUPPLIER_CODE_MAX_LENGTH)
    card_type: str = Field(max_length=CARD_TYPE_MAX_LENGTH)


class CardOperationUpdateSchema(CustomBaseModel):
    id: str = Field(max_length=CARD_ID_MAX_LENGTH)
    fabric_id: str = Field(max_length=FABRIC_ID_MAX_LENGTH)
    net_weight: float
