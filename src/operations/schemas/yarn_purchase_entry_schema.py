from pydantic import Field

from datetime import date, datetime

from src.core.schemas import CustomBaseModel

from .yarn_purchase_entry_detalle_schema import (
    YarnPurchaseEntryDetalleSimpleSchema
)

class YarnPurchaseEntryBase(CustomBaseModel):
    # storage_code: str
    # movement_type: str
    # movement_code: str
    # document_code: str
    entry_number: str | None = Field(alias="document_number")
    period: int
    creation_date: date | None
    creation_time: str | None
    supplier_code: str | None = Field(default=None, alias="auxiliary_code")
    status_flag: str | None
    purchase_order_number: str | None = Field(default=None, alias="reference_number")
    flgtras: bool | None
    supplier_batch: str | None
    mecsa_batch: str | None

    class Config:
        from_attributes = True

class YarnPurchaseEntrySimpleSchema(YarnPurchaseEntryBase):
    pass

class YarnPurchaseEntriesSimpleListSchema(CustomBaseModel):
    yarn_purchase_entries: list[YarnPurchaseEntryBase] = []

class YarnPurchaseEntrySearchSchema(CustomBaseModel):
    period: int = Field(default=datetime.now().year)

class YarnPurchaseEntrySchema(YarnPurchaseEntrySimpleSchema):
    currency_code: int | None
    exchange_rate: float | None
    document_note: str | None
    supplier_po_correlative: str | None = Field(default=None, alias="nrogf")
    supplier_po_series: str | None = Field(default=None, alias="sergf")
    fecgf: date | None
    voucher_number: str | None
    fchcp: date | None
    flgcbd: str | None
    serial_number_po: str | None = Field(default=None, alias="serial_number")
    printed_flag: str | None

    detalle: list[YarnPurchaseEntryDetalleSimpleSchema] = []
