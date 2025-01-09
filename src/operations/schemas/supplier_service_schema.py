from src.core.schemas import CustomBaseModel


class SupplierServiceBase(CustomBaseModel):
    supplier_code: str | None
    service_code: str | None
    sequence_number: int | None = None

    class Config:
        from_attributes = True


class SupplierServiceSimpleSchema(SupplierServiceBase):
    pass


class SupplierServiceSchema(SupplierServiceSimpleSchema):
    pass
