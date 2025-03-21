from datetime import date

from pydantic import (
    AliasChoices,
    Field,
    computed_field,
)

from src.core.constants import PAGE_SIZE
from src.core.schemas import CustomBaseModel
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    DOCUMENT_NOTE_MAX_LENGTH,
    NRODIR_MAX_LENGTH,
    SUPPLIER_CODE_MAX_LENGTH,
    SUPPLIER_COLOR_ID_MAX_LENGTH,
)

from .dyeing_service_dispatch_detail_schema import (
    DyeingServiceDispatchDetailCreateSchema,
    DyeingServiceDispatchDetailSchema,
    DyeingServiceDispatchDetailUpdateSchema,
)


class DyeingServiceDispatchBase(CustomBaseModel):
    dispatch_number: str | None = Field(
        default=None, validation_alias="document_number"
    )
    period: int | None = None
    creation_date: date | None = None
    creation_time: str | None = None
    supplier_code: str | None = Field(default=None, validation_alias="auxiliary_code")
    status_flag: str | None = None

    class Config:
        from_attributes = True


class DyeingServiceDispatchSchema(DyeingServiceDispatchBase):
    document_note: str | None = None
    user_id: str | None = None
    tint_supplier_color_id: str | None = Field(
        default=None, validation_alias="empqnro2"
    )
    nrodir: str | None = Field(default=None, validation_alias="nrodir2")

    detail: list[DyeingServiceDispatchDetailSchema] = Field(
        default=None, validation_alias="detail_dyeing"
    )


class DyeingServiceDispatchesListSchema(CustomBaseModel):
    dyeing_service_dispatches: list[DyeingServiceDispatchSchema] = []


class DyeingServiceDispatchFilterParams(CustomBaseModel):
    period: int | None = Field(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    )
    page: int | None = Field(default=1, ge=1)
    include_annulled: bool | None = Field(default=False)

    @computed_field
    def limit(self) -> int:
        return PAGE_SIZE

    @computed_field
    def offset(self) -> int:
        return (self.page - 1) * PAGE_SIZE


class DyeingServiceDispatchCreateSchema(CustomBaseModel):
    supplier_id: str = Field(max_length=SUPPLIER_CODE_MAX_LENGTH)
    nrodir: str | None = Field(default="000", max_length=NRODIR_MAX_LENGTH)
    period: int
    tint_supplier_color_id: str = Field(max_length=SUPPLIER_COLOR_ID_MAX_LENGTH)
    document_note: str | None = Field(default=None, max_length=DOCUMENT_NOTE_MAX_LENGTH)

    detail: list[DyeingServiceDispatchDetailCreateSchema] = []


class DyeingServiceDispatchUpdateSchema(CustomBaseModel):
    supplier_id: str = Field(max_length=SUPPLIER_CODE_MAX_LENGTH)
    nrodir: str | None = Field(default="000", max_length=NRODIR_MAX_LENGTH)
    tint_supplier_color_id: str = Field(max_length=SUPPLIER_COLOR_ID_MAX_LENGTH)
    document_note: str | None = Field(default=None, max_length=DOCUMENT_NOTE_MAX_LENGTH)

    detail: list[DyeingServiceDispatchDetailUpdateSchema] = []
