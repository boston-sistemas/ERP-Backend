from datetime import date, datetime

from pydantic import AliasChoices, Field

from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    NROGF_MAX_LENGTH,
    REFERENCE_NUMBER_MAX_LENGTH,
    SERGF_MAX_LENGTH,
)

from .yarn_purchase_entry_detail_schema import (
    YarnPurchaseEntryDetalleCreateSchema,
    YarnPurchaseEntryDetalleSimpleSchema,
)


class YarnPurchaseEntryBase(CustomBaseModel):
    # storage_code: str
    # movement_type: str
    # movement_code: str
    # document_code: str
    entry_number: str | None = Field(
        validation_alias=AliasChoices("document_number", "entry_number")
    )
    period: int
    creation_date: date | None
    creation_time: str | None
    supplier_code: str | None = Field(
        default=None, validation_alias=AliasChoices("auxiliary_code", "supplier_code")
    )
    status_flag: str | None
    purchase_order_number: str | None = Field(
        default=None,
        validation_alias=AliasChoices("reference_number", "purchase_order_number"),
    )
    flgtras: bool | None
    supplier_batch: str | None
    mecsa_batch: str | None

    document_note: str | None

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
    supplier_po_correlative: str | None = Field(
        default=None, validation_alias=AliasChoices("nrogf", "supplier_po_correlative")
    )
    supplier_po_series: str | None = Field(
        default=None,
        validation_alias=AliasChoices("sergf", "supplier_po_series"),
    )
    fecgf: date | None
    voucher_number: str | None
    fchcp: date | None
    flgcbd: str | None
    serial_number_po: str | None = Field(
        default=None, validation_alias=AliasChoices("serial_number", "serial_number_po")
    )
    printed_flag: str | None

    detail: list[YarnPurchaseEntryDetalleSimpleSchema] = []


class YarnPurchaseEntryCreateSchema(CustomBaseModel):
    period: int
    supplier_po_correlative: str = Field(max_length=NROGF_MAX_LENGTH)
    supplier_po_series: str = Field(max_length=SERGF_MAX_LENGTH)
    fecgf: date
    purchase_order_number: str = Field(max_length=REFERENCE_NUMBER_MAX_LENGTH)
    document_note: str | None = None

    detail: list[YarnPurchaseEntryDetalleCreateSchema] = Field(default=[])
