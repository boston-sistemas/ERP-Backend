from src.core.schemas import CustomBaseModel


class SupplierColorBase(CustomBaseModel):
    id: str | None = None
    description: str | None = None

    class Config:
        from_attributes = True


class SupplierColorSchema(SupplierColorBase):
    pass
