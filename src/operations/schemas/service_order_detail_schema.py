from src.core.schemas import CustomBaseModel
from pydantic import Field, AliasChoices

class ServiceOrderDetailBase(CustomBaseModel):
    tissue_id: str | None = Field(
        validation_alias="product_id"
    )
    quantity_ordered: float | None = None
    quantity_supplied: float | None = None
    price: float | None = None

    class Config:
        from_attributes = True

class ServiceOrderDetailSimpleSchema(ServiceOrderDetailBase):
    pass

class ServiceOrderDetailSchema(ServiceOrderDetailSimpleSchema):
    pass

class ServiceOrderDetailCreateSchema(CustomBaseModel):
    tissue_id: str
    quantity_ordered: float = Field(gt=0)
    price: float = Field(gt=0)

class ServiceOrderDetailUpdateSchema(ServiceOrderDetailCreateSchema):
    pass
