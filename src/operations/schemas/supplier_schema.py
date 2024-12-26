from src.core.schemas import CustomBaseModel

from .supplier_service_schema import SupplierServiceSchema

from pydantic import Field

class SupplierBase(CustomBaseModel):
    code: str | None
    name: str | None
    address: str | None
    ruc: str | None
    is_active: str | None
    storage_code: str | None = None
    initials: str | None = None

    class Config:
        from_attributes = True


class SupplierSimpleSchema(SupplierBase):
    pass


class SupplierSchema(SupplierSimpleSchema):
    services: list[SupplierServiceSchema] | None = []
