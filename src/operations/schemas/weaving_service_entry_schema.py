from datetime import date

from pydantic import Field, model_validator

from src.core.schemas import CustomBaseModel

from .weaving_service_entry_detail_schema import (
    WeavingServiceEntryDetailSchema,
    WeavingServiceEntryDetailCreateSchema,
    WeavingServiceEntryDetailUpdateSchema,
)

from src.operations.constants import (
    DOCUMENT_NOTE_MAX_LENGTH,
    NROGF_MAX_LENGTH,
    REFERENCE_NUMBER_MAX_LENGTH,
    SERGF_MAX_LENGTH,
    SUPPLIER_CODE_MAX_LENGTH,
)

class WeavingServiceEntryBase(CustomBaseModel):
    entry_number: str | None = Field(default=None, validation_alias="document_number")
    period: int | None = None
    creation_date: date | None = None
    creation_time: str | None = None
    supplier_code: str | None = Field(default=None, validation_alias="auxiliary_code")
    status_flag: str | None = None

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

    detail: list[WeavingServiceEntryDetailSchema] = []


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

class WeavingServiceEntryUpdateSchema(WeavingServiceEntryCreateSchema):
    detail: list[WeavingServiceEntryDetailUpdateSchema] = Field(default=[])
