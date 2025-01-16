from datetime import date

from pydantic import Field, field_serializer

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
    status_flag: str | None = Field(exclude=True)
    status_param_id: int | None = None

    @field_serializer("issue_date", when_used="json")
    def serialize_creation_date(value: date | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

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


class ServiceOrderFilterParams(CustomBaseModel):
    supplier_ids: list[str] | None = Field(default=None)
    limit: int | None = Field(default=10, ge=1, le=100)
    offset: int | None = Field(default=0, ge=0)
    include_annulled: bool | None = Field(default=False)
    include_detail: bool | None = Field(default=False)


class ServiceOrderCreateSchema(CustomBaseModel):
    supplier_id: str
    detail: list[ServiceOrderDetailCreateSchema] = []


class ServiceOrderUpdateSchema(CustomBaseModel):
    status_param_id: int
    detail: list[ServiceOrderDetailUpdateSchema] = []
