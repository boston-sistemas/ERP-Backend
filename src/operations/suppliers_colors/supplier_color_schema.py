from src.core.schemas import CustomBaseModel


class SupplierColorBase(CustomBaseModel):
    id: str | None = None
    supplier_id: str | None = None
    description: str | None = None

    class Config:
        from_attributes = True


class SupplierColorSchema(SupplierColorBase):
    pass


class SupplierColorListSchema(CustomBaseModel):
    supplier_colors: list[SupplierColorSchema]
