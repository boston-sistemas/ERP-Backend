from datetime import date

from pydantic import Field, computed_field, model_validator

from src.core.constants import PAGE_SIZE
from src.core.schemas import CustomBaseModel
from src.core.utils import PERU_TIMEZONE, calculate_time

from .orden_compra_detalle_schema import (
    OrdenCompraDetalleBase,
    YarnPurchaseOrderDetailSchema,
)
from .promec_schema import (
    PromecCurrencySchema,
    PromecStatusSchema,
)


class OrdenCompraBase(CustomBaseModel):
    company_code: str
    purchase_order_type: str
    purchase_order_number: str
    supplier_code: str
    issue_date: date | None
    due_date: date | None
    payment_method: str | None
    status_flag: str | None = Field(exclude=True)
    currency_code: int | None = Field(exclude=True)

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
    promec_currency: PromecCurrencySchema | None = Field(default=None)

    @model_validator(mode="after")
    def set_promec_currency(self):
        if self.currency_code is not None:
            self.promec_currency = PromecCurrencySchema(currency_id=self.currency_code)
        return self

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


class PurchaseOrderFilterParams(CustomBaseModel):
    period: int | None = Field(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    )
    include_detail: bool = Field(default=False)
    page: int | None = Field(default=1, ge=1)

    @computed_field
    def limit(self) -> int:
        return PAGE_SIZE

    @computed_field
    def offset(self) -> int:
        return (self.page - 1) * PAGE_SIZE
