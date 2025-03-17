from datetime import date

from pydantic import Field, computed_field, field_serializer

from src.core.constants import PAGE_SIZE
from src.core.schemas import CustomBaseModel
from src.core.utils import PERU_TIMEZONE, calculate_time
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
    period: int | None = Field(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    )
    include_annulled: bool | None = Field(default=False)

    page: int | None = Field(default=1, ge=1)

    @computed_field
    def limit(self) -> int:
        return PAGE_SIZE

    @computed_field
    def offset(self) -> int:
        return (self.page - 1) * PAGE_SIZE


class ServiceOrderCreateSchema(CustomBaseModel):
    supplier_id: str
    detail: list[ServiceOrderDetailCreateSchema] = []


class ServiceOrderUpdateSchema(CustomBaseModel):
    detail: list[ServiceOrderDetailUpdateSchema] = []


class ServiceOrderSupplyDetailSchema(CustomBaseModel):
    service_order_id: str | None = Field(
        default=None, validation_alias="reference_number"
    )
    creation_date: date | None = None
    yarn_id: str | None = Field(default=None, validation_alias="product_code1")
    quantity_dispatched: float | None = None
    quantity_received: float | None = None
    status_flag: str | None = None

    class Config:
        from_attributes = True


class ServiceOrderProgressReviewListSchema(CustomBaseModel):
    service_orders_progress: list[ServiceOrderSupplyDetailSchema] | None = []
