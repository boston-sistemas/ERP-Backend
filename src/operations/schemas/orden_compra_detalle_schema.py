from pydantic import AliasChoices, Field

from src.core.schemas import CustomBaseModel

from .yarn_schema import YarnSchema


class OrdenCompraDetalleBase(CustomBaseModel):
    quantity_ordered: float
    quantity_supplied: float
    unit_code: str
    precto: float
    impcto: float
    yarn: YarnSchema | None
    status_flag: str | None = "P"
    yarn_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("product_code", "yarn_id"),
        exclude=True,
    )

    class Config:
        from_attributes = True


# class OrdenCompraDetalleCreateSchema(OrdenCompraDetalleBase):
#     pass
