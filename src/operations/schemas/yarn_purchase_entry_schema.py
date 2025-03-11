from datetime import date, datetime

from pydantic import (
    AliasChoices,
    Field,
    computed_field,
    field_serializer,
    model_validator,
)

from src.core.constants import PAGE_SIZE
from src.core.schemas import CustomBaseModel
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    DOCUMENT_NOTE_MAX_LENGTH,
    NROGF_MAX_LENGTH,
    REFERENCE_NUMBER_MAX_LENGTH,
    SERGF_MAX_LENGTH,
    SUPPLIER_BATCH_MAX_LENGTH,
)

from .orden_compra_schema import OrdenCompraWithDetailSchema
from .promec_schema import PromecStatusSchema
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
    entry_number: str | None = Field(validation_alias=AliasChoices("document_number"))
    period: int
    creation_date: date | None
    creation_time: str | None
    supplier_code: str | None = Field(
        default=None, validation_alias=AliasChoices("auxiliary_code", "supplier_code")
    )
    purchase_order_number: str | None = Field(
        default=None,
        validation_alias=AliasChoices("reference_number2", "purchase_order_number"),
    )
    flgtras: bool | None
    supplier_batch: str | None
    mecsa_batch: str | None

    document_note: str | None

    @field_serializer("creation_date", when_used="json")
    def serialize_creation_date(value: date | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

    @field_serializer("supplier_code")
    def serialize_supplier_batch(value: str | None) -> str | None:
        return value.upper() if value is not None else None

    class Config:
        from_attributes = True


class YarnPurchaseEntrySimpleSchema(YarnPurchaseEntryBase):
    status_flag: str | None = Field(exclude=True)

    promec_status: PromecStatusSchema | None = Field(default=None)

    @model_validator(mode="after")
    def set_promec_status(self):
        if self.status_flag is not None:
            self.promec_status = PromecStatusSchema(status_id=self.status_flag)
        return self


class YarnPurchaseEntryFilterParams(CustomBaseModel):
    period: int | None = Field(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    )
    entry_number: str | None = Field(default=None)
    supplier_ids: list[str] | None = Field(default=None)
    purchase_order_number: str | None = Field(default=None)
    supplier_batch: str | None = Field(default=None)
    mecsa_batch: str | None = Field(default=None)
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    include_annulled: bool | None = Field(default=False)
    page: int | None = Field(default=1, ge=1)

    @computed_field
    # @property
    def limit(self) -> int:
        return PAGE_SIZE

    @computed_field
    # @property
    def offset(self) -> int:
        return (self.page - 1) * PAGE_SIZE


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


class YarnPurchaseEntryPrintSchema(CustomBaseModel):
    entry_number: str
    include_heave: bool | None = Field(default=False)


class YarnPurchaseEntryPrintListSchema(CustomBaseModel):
    entry_numbers: list[YarnPurchaseEntryPrintSchema] = []


class YarnPurchaseEntryCreateSchema(CustomBaseModel):
    # period: int
    supplier_po_correlative: str = Field(min_length=1, max_length=NROGF_MAX_LENGTH)
    supplier_po_series: str = Field(min_length=1, max_length=SERGF_MAX_LENGTH)
    fecgf: date
    purchase_order_number: str = Field(
        min_length=1, max_length=REFERENCE_NUMBER_MAX_LENGTH
    )
    document_note: str | None = Field("", max_length=DOCUMENT_NOTE_MAX_LENGTH)
    supplier_batch: str = Field(min_length=1, max_length=SUPPLIER_BATCH_MAX_LENGTH)

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
    document_note: str | None = Field("", max_length=DOCUMENT_NOTE_MAX_LENGTH)
    supplier_batch: str = Field(max_length=SUPPLIER_BATCH_MAX_LENGTH)
    detail: list[YarnPurchaseEntryDetailUpdateSchema] = Field(default=[])
