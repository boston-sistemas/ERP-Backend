
from src.core.schemas import CustomBaseModel

# Schema Temp
class YarnSchema(CustomBaseModel):
    codcia: str
    yarn_code: str
    family_code: str
    subfamily_code: str
    details: str | None

    class Config:
        from_attributes = True

class OrdenCompraDetalleBase(CustomBaseModel):
    codcia: str
    purchase_order_type: str
    purchase_order_number: str
    product_code: str
    quantity_ordered: float
    quantity_supplied: float
    status_flag: str
    unit_code: str
    yarn: YarnSchema | None

    class Config:
        from_attributes = True

# class OrdenCompraDetalleCreateSchema(OrdenCompraDetalleBase):
#     pass
