from datetime import date

from pydantic import Field

from src.core.schemas import CustomBaseModel

from .orden_compra_detalle_schema import OrdenCompraDetalleBase

# from pydantic import field_serializer


class OrdenCompraBase(CustomBaseModel):
    company_code: str
    purchase_order_type: str
    purchase_order_number: str
    supplier_code: str
    issue_date: date | None
    due_date: date | None
    payment_method: str | None
    status_flag: str
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


class OrdenCompraWithDetailSchema(OrdenCompraBase):
    detail: list[OrdenCompraDetalleBase] | None = Field([])


class OrdenCompraWithDetallesListSchema(CustomBaseModel):
    ordenes: list[OrdenCompraWithDetailSchema]
