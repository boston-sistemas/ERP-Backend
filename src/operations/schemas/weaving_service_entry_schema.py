from datetime import date

from pydantic import Field

from src.core.schemas import CustomBaseModel

from .weaving_service_entry_detail_schema import (
    WeavingServiceEntryDetailSchema,
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


class WeavingServiceEntryCreateSchema(WeavingServiceEntryBase):
    pass


class WeavingServiceEntryUpdateSchema(WeavingServiceEntryBase):
    pass
