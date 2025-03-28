from pydantic import Field

from src.core.schemas import CustomBaseModel


class SupplierColorBase(CustomBaseModel):
    id: str | None = None
    supplier_id: str | None = None
    description: str | None = None
    mecsa_color_id: str | None = None
    is_active: bool | None

    class Config:
        from_attributes = True


class SupplierColorSchema(SupplierColorBase):
    pass


class SupplierColorListSchema(CustomBaseModel):
    supplier_colors: list[SupplierColorSchema]


class SupplierColorUpdateSchema(CustomBaseModel):
    description: str | None = None


class SupplierColorFilterParams(CustomBaseModel):
    supplier_ids: list[str] | None = Field(default=None)
    mecsa_color_id: str | None = None
