from datetime import date

from src.core.schemas import CustomBaseModel
from src.security.schemas import ParameterValueSchema

from .service_order_detail_schema import (
    ServiceOrderDetailCreateSchema,
    ServiceOrderDetailSchema,
    ServiceOrderDetailUpdateSchema,
)


class ServiceOrderBase(CustomBaseModel):
    id: str | None = None
    supplier_id: str | None = None
    issue_date: date | None = None
    due_date: date | None = None
    storage_code: str | None = None
    status_flag: str | None = None
    status_param_id: int | None = None

    class Config:
        from_attributes = True


class ServiceOrderSimpleSchema(ServiceOrderBase):
    status: ParameterValueSchema | None = None


class ServiceOrderSimpleListSchema(CustomBaseModel):
    service_orders: list[ServiceOrderSimpleSchema] | None = []


class ServiceOrderSchema(ServiceOrderSimpleSchema):
    detail: list[ServiceOrderDetailSchema] | None = []


class ServiceOrderListSchema(CustomBaseModel):
    service_orders: list[ServiceOrderSchema] | None = []


class ServiceOrderCreateSchema(CustomBaseModel):
    supplier_id: str
    detail: list[ServiceOrderDetailCreateSchema] = []


class ServiceOrderUpdateSchema(CustomBaseModel):
    status_param_id: int
    detail: list[ServiceOrderDetailUpdateSchema] = []
