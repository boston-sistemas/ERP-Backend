from src.core.schemas import CustomBaseModel


class SupplierServiceBase(CustomBaseModel):
    supplier_code: str | None
    service_code: str | None

    class Config:
        from_attributes = True


class SupplierServiceSimpleSchema(SupplierServiceBase):
    pass


class SupplierServiceSchema(SupplierServiceSimpleSchema):
    pass
