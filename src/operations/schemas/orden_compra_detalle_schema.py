
from src.core.schemas import CustomBaseModel

# Schema Temp
class YarnSchema(CustomBaseModel):
    yarn_code: str
    details: str | None

    class Config:
        from_attributes = True

class OrdenCompraDetalleBase(CustomBaseModel):
    quantity_ordered: float
    quantity_supplied: float
    unit_code: str
    yarn: YarnSchema | None

    class Config:
        from_attributes = True

# class OrdenCompraDetalleCreateSchema(OrdenCompraDetalleBase):
#     pass
