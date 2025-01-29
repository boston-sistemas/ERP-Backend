from datetime import date

from pydantic import Field, model_validator

from src.core.schemas import CustomBaseModel

from .orden_compra_detalle_schema import (
    OrdenCompraDetalleBase,
    YarnPurchaseOrderDetailSchema,
)
from .promec_status_schema import PromecStatusSchema


class OrdenCompraBase(CustomBaseModel):
    company_code: str
    purchase_order_type: str
    purchase_order_number: str
    supplier_code: str
    issue_date: date | None
    due_date: date | None
    payment_method: str | None
    status_flag: str | None = Field(exclude=True)
    currency_code: int

    class Config:
        from_attributes = True

    # @field_serializer('issue_date', 'due_date')
    # def serialize_dates(self, value):
    #     if value is not None:
    #         return value.strftime('%Y-%m-%d')
    #     return None


class OrdenCompraSimpleSchema(OrdenCompraBase):
    pass


class YarnPurchaseOrderSchema(OrdenCompraBase):
    promec_status: PromecStatusSchema | None = Field(default=None)

    @model_validator(mode="after")
    def set_promec_status(self):
        if self.status_flag is not None:
            self.promec_status = PromecStatusSchema(status_id=self.status_flag)
        return self

    detail: list[YarnPurchaseOrderDetailSchema] | None = Field([])


class OrdenCompraWithDetailSchema(OrdenCompraBase):
    detail: list[OrdenCompraDetalleBase] | None = Field([])


class OrdenCompraWithDetallesListSchema(CustomBaseModel):
    ordenes: list[OrdenCompraWithDetailSchema]


class YarnPurchaseOrderListSchema(CustomBaseModel):
    yarn_orders: list[YarnPurchaseOrderSchema] | None = []
