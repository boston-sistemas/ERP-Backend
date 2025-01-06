from typing import Any

from pydantic import Field, model_validator

from src.core.schemas import CustomBaseModel

from .supplier_service_schema import SupplierServiceSchema
from .supplier_color_schema import SupplierColorSchema

class SupplierBase(CustomBaseModel):
    code: str | None
    name: str | None
    ruc: str | None
    is_active: str | None
    storage_code: str | None = None
    initials: str | None = None

    class Config:
        from_attributes = True


class SupplierSimpleSchema(SupplierBase):
    email: str | None = Field(None, exclude=True)
    emails: list[str] | None = []

    address: str | None = Field(default=None, exclude=True)
    other_addresses: Any | None = Field(default=None, exclude=True)

    addresses: dict | None = []

    @model_validator(mode="after")
    def asign_addresses(self):
        addresses = {}
        if self.address:
            addresses["000"] = self.address

        if self.other_addresses:
            for address in self.other_addresses:
                if isinstance(address.address, str) and isinstance(address.nrodir, str):
                    addresses[address.nrodir] = address.address

        self.addresses = addresses

        return self

    @model_validator(mode="after")
    def asign_emails(self):
        if isinstance(self.email, str):
            self.emails = self.email.split(";")
        return self


class SupplierSimpleListSchema(CustomBaseModel):
    suppliers: list[SupplierSimpleSchema] = []


class SupplierSchema(SupplierSimpleSchema):
    services: list[SupplierServiceSchema] | None = []
    colors: list[SupplierColorSchema] | None = []
