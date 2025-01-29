from datetime import date

from pydantic import Field, field_serializer, model_validator

from src.core.schemas import CustomBaseModel
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    CARD_ID_MAX_LENGTH,
    DOCUMENT_NOTE_MAX_LENGTH,
    NROGF_MAX_LENGTH,
    SERGF_MAX_LENGTH,
    SUPPLIER_CODE_MAX_LENGTH,
)

from .promec_status_schema import PromecStatusSchema
from .weaving_service_entry_detail_schema import (
    WeavingServiceEntryDetailCreateSchema,
    WeavingServiceEntryDetailSchema,
    WeavingServiceEntryDetailUpdateSchema,
)


class WeavingServiceEntryBase(CustomBaseModel):
    entry_number: str | None = Field(default=None, validation_alias="document_number")
    period: int | None = None
    creation_date: date | None = None
    creation_time: str | None = None
    supplier_code: str | None = Field(default=None, validation_alias="auxiliary_code")

    @field_serializer("creation_date", when_used="json")
    def serialize_creation_date(value: date | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

    class Config:
        from_attributes = True


class WeavingServiceEntrySimpleSchema(WeavingServiceEntryBase):
    pass


class WeavingServiceEntriesSimpleListSchema(CustomBaseModel):
    weaving_service_entries: list[WeavingServiceEntrySimpleSchema] = []


class WeavingServiceEntrySchema(WeavingServiceEntrySimpleSchema):
    # supplier_batch: str | None = None
    # mecsa_batch: str | None = None
    supplier_po_correlative: str | None = Field(default=None, validation_alias="nrogf")
    supplier_po_series: str | None = Field(default=None, validation_alias="sergf")
    document_note: str | None = None
    fecgf: date | None
    user_id: str | None = None

    status_flag: str | None = Field(exclude=True)

    promec_status: PromecStatusSchema | None = Field(default=None)

    @model_validator(mode="after")
    def set_promec_status(self):
        if self.status_flag is not None:
            self.promec_status = PromecStatusSchema(status_id=self.status_flag)
        return self

    detail: list[WeavingServiceEntryDetailSchema] = []


class WeavingServiceEntriesListSchema(CustomBaseModel):
    weaving_service_entries: list[WeavingServiceEntrySchema] = []


class WeavingServiceEntryFilterParams(CustomBaseModel):
    period: int | None = Field(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    )
    entry_number: str | None = Field(default=None)
    supplier_ids: list[str] | None = Field(default=None)
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    limit: int | None = Field(default=10, ge=1, le=100)
    offset: int | None = Field(default=0, ge=0)
    include_annulled: bool | None = Field(default=False)


class WeavingServiceEntryCreateSchema(CustomBaseModel):
    period: int
    supplier_po_correlative: str = Field(max_length=NROGF_MAX_LENGTH)
    supplier_po_series: str = Field(max_length=SERGF_MAX_LENGTH)
    document_note: str | None = Field(None, max_length=DOCUMENT_NOTE_MAX_LENGTH)
    supplier_id: str = Field(max_length=SUPPLIER_CODE_MAX_LENGTH)
    fecgf: date

    generate_cards: bool | None = Field(default=False)
    detail: list[WeavingServiceEntryDetailCreateSchema] = []

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


class WeavingServiceEntryPrintSchema(CustomBaseModel):
    card_id: str = Field(max_length=CARD_ID_MAX_LENGTH)


class WeavingServiceEntryPrintListSchema(CustomBaseModel):
    card_ids: list[WeavingServiceEntryPrintSchema] = []


class WeavingServiceEntryUpdateSchema(CustomBaseModel):
    supplier_po_correlative: str = Field(max_length=NROGF_MAX_LENGTH)
    supplier_po_series: str = Field(max_length=SERGF_MAX_LENGTH)
    document_note: str | None = Field(None, max_length=DOCUMENT_NOTE_MAX_LENGTH)
    supplier_id: str = Field(max_length=SUPPLIER_CODE_MAX_LENGTH)
    fecgf: date

    generate_cards: bool | None = Field(default=False)
    detail: list[WeavingServiceEntryDetailUpdateSchema] = Field(default=[])
