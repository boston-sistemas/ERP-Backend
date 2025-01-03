from pydantic import Field

from src.core.schemas import CustomBaseModel
from src.security.schemas import ParameterValueSchema


class ServiceOrderDetailBase(CustomBaseModel):
    tissue_id: str | None = Field(validation_alias="product_id")
    quantity_ordered: float | None = None
    quantity_supplied: float | None = None
    price: float | None = None
    status_param_id: int | None = None

    class Config:
        from_attributes = True


class ServiceOrderDetailSimpleSchema(ServiceOrderDetailBase):
    status: ParameterValueSchema | None = None


class ServiceOrderDetailSchema(ServiceOrderDetailSimpleSchema):
    pass


class ServiceOrderDetailCreateSchema(CustomBaseModel):
    tissue_id: str
    quantity_ordered: float = Field(gt=0)
    price: float = Field(gt=0)


class ServiceOrderDetailUpdateSchema(ServiceOrderDetailCreateSchema):
    pass
