from src.core.schemas import CustomBaseModel
from pydantic import model_validator, Field
from .supplier_service_schema import SupplierServiceSchema


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
    email: str | None = Field(None, exclude=True)
    emails: list[str] | None = []

    @model_validator(mode="after")
    def asign_emails(self):
        if isinstance(self.email, str):
            self.emails = self.email.split(";")
        return self

class SupplierSimpleListSchema(CustomBaseModel):
    suppliers: list[SupplierSimpleSchema] = []

class SupplierSchema(SupplierSimpleSchema):
    services: list[SupplierServiceSchema] | None = []
