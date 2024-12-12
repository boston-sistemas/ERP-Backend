from src.core.schemas import CustomBaseModel
from src.operations.schemas import YarnSchema


class OrdenCompraDetalleBase(CustomBaseModel):
    quantity_ordered: float
    quantity_supplied: float
    unit_code: str
    yarn: YarnSchema | None

    class Config:
        from_attributes = True


# class OrdenCompraDetalleCreateSchema(OrdenCompraDetalleBase):
#     pass
