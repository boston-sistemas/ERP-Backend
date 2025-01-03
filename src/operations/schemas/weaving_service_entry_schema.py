from datetime import date, datetime

from pydantic import Field, model_validator
from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    DOCUMENT_NOTE_MAX_LENGTH,
    NROGF_MAX_LENGTH,
    REFERENCE_NUMBER_MAX_LENGTH,
    SERGF_MAX_LENGTH,
    SUPPLIER_BATCH_MAX_LENGTH,
)

class WeavingServiceEntryBase(CustomBaseModel):
    entry_number: str | None = Field(
        default=None,
        validation_alias="document_number"
    )
    period: int | None = None
    creation_date: date | None = None
    creation_time: str | None = None
    supplier_code: str | None = Field(
        default=None, validation_alias="auxiliary_code"
    )
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
    supplier_po_correlative: str | None = Field(
        default=None, validation_alias="nrogf"
    )
    supplier_po_series: str | None = Field(
        default=None,
        validation_alias="sergf"
    )
    document_note: str | None = None
    fecgf: date | None
    user_id: str | None = None

class WeavingServiceEntryCreateSchema(WeavingServiceEntryBase):
    pass

class WeavingServiceEntryUpdateSchema(WeavingServiceEntryBase):
    pass


