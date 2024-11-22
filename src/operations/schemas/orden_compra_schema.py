from datetime import datetime

from pydantic import BaseModel

from .orden_compra_detalle_schema import OrdenCompraDetalleBase

class OrdenCompraBase(BaseModel):
    codcia: str
    purchase_order_type: str
    purchase_order_number: str
    supplier_code: str
    issue_date: datetime | None
    due_date: datetime | None
    payment_method: str | None
    status_flag: str
    currency_code: int

    class Config:
        from_attributes = True

class OrdenCompraSimpleSchema(OrdenCompraBase):
    pass

class OrdenCompraWithDetallesSchema(OrdenCompraBase):
    detalle: list[OrdenCompraDetalleBase] = []

class OrdenCompraWithDetallesListSchema(BaseModel):
    ordenes: list[OrdenCompraWithDetallesSchema]
