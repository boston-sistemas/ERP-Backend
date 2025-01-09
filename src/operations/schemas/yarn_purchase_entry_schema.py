from datetime import date, datetime

from pydantic import AliasChoices, Field, model_validator

from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    DOCUMENT_NOTE_MAX_LENGTH,
    NROGF_MAX_LENGTH,
    REFERENCE_NUMBER_MAX_LENGTH,
    SERGF_MAX_LENGTH,
    SUPPLIER_BATCH_MAX_LENGTH,
)

from .orden_compra_schema import OrdenCompraWithDetailSchema
from .yarn_purchase_entry_detail_schema import (
    YarnPurchaseEntryDetailCreateSchema,
    YarnPurchaseEntryDetailSimpleSchema,
    YarnPurchaseEntryDetailUpdateSchema,
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
        validation_alias=AliasChoices("reference_number2", "purchase_order_number"),
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
    yarn_purchase_entries: list[YarnPurchaseEntrySimpleSchema] = []


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

    detail: list[YarnPurchaseEntryDetailSimpleSchema] = []
    purcharse_order: OrdenCompraWithDetailSchema | None = Field(
        default=None, exclude=True
    )


class YarnPurchaseEntryCreateSchema(CustomBaseModel):
    period: int
    supplier_po_correlative: str = Field(max_length=NROGF_MAX_LENGTH)
    supplier_po_series: str = Field(max_length=SERGF_MAX_LENGTH)
    fecgf: date
    purchase_order_number: str = Field(max_length=REFERENCE_NUMBER_MAX_LENGTH)
    document_note: str | None = Field(None, max_length=DOCUMENT_NOTE_MAX_LENGTH)
    supplier_batch: str = Field(max_length=SUPPLIER_BATCH_MAX_LENGTH)

    detail: list[YarnPurchaseEntryDetailCreateSchema] = Field(default=[])

    @model_validator(mode="after")
    def align_item_numbers(self):
        total = len(self.detail)
        assigned_nums = [
            d.item_number for d in self.detail if d.item_number is not None
        ]

        if len(assigned_nums) != len(set(assigned_nums)) or any(
            num < 1 or num > total for num in assigned_nums
        ):
            for i, d in enumerate(self.detail, start=1):
                d.item_number = i
            return self

        used = set(assigned_nums)
        missing = [i for i in range(1, total + 1) if i not in used]

        m_idx = 0
        for d in self.detail:
            if d.item_number is None:
                d.item_number = missing[m_idx]
                m_idx += 1

        return self


class YarnPurchaseEntryUpdateSchema(CustomBaseModel):
    supplier_po_correlative: str = Field(max_length=NROGF_MAX_LENGTH)
    supplier_po_series: str = Field(max_length=SERGF_MAX_LENGTH)
    fecgf: date
    document_note: str | None = Field(None, max_length=DOCUMENT_NOTE_MAX_LENGTH)
    supplier_batch: str = Field(max_length=SUPPLIER_BATCH_MAX_LENGTH)
    detail: list[YarnPurchaseEntryDetailUpdateSchema] = Field(default=[])

    @model_validator(mode="after")
    def align_item_numbers(self):
        total = len(self.detail)
        assigned_nums = [
            d.item_number for d in self.detail if d.item_number is not None
        ]

        if len(assigned_nums) != len(set(assigned_nums)) or any(
            num < 1 or num > total for num in assigned_nums
        ):
            for i, d in enumerate(self.detail, start=1):
                d.item_number = i
            return self

        used = set(assigned_nums)
        missing = [i for i in range(1, total + 1) if i not in used]

        m_idx = 0
        for d in self.detail:
            if d.item_number is None:
                d.item_number = missing[m_idx]
                m_idx += 1

        return self
