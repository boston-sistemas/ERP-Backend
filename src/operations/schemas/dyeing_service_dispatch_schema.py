from datetime import date

from pydantic import Field, model_validator

from src.core.schemas import CustomBaseModel

from .dyeing_service_dispatch_detail_schema import (
    DyeingServiceDispatchDetailSchema,
    DyeingServiceDispatchDetailCreateSchema,
    DyeingServiceDispatchDetailUpdateSchema,
)

class DyeingServiceDispatchBase(CustomBaseModel):

    dispatch_number: str | None = Field(default=None, validation_alias="document_number")
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
    tint_supplier_color_id: str | None = Field(default=None, validation_alias="empqnro2")
    nrodir: str | None = Field(default=None, validation_alias="nrodir2")

    detail: list[DyeingServiceDispatchDetailSchema] = Field(
        default=None, validation_alias="detail_dyeing"
    )

class DyeingServiceDispatchesListSchema(CustomBaseModel):
    dyeing_service_dispatches: list[DyeingServiceDispatchSchema] = []

class DyeingServiceDispatchCreateSchema(CustomBaseModel):
    pass

class DyeingServiceDispatchUpdateSchema(CustomBaseModel):
    pass
