from datetime import date

from pydantic import AliasChoices, Field, field_serializer, model_validator

from src.core.schemas import CustomBaseModel
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    DOCUMENT_NOTE_MAX_LENGTH,
    NRODIR_MAX_LENGTH,
    SERVICE_ORDER_ID_MAX_LENGTH,
)

from .promec_status_schema import PromecStatusSchema
from .yarn_weaving_dispatch_detail_schema import (
    YarnWeavingDispatchDetailCreateSchema,
    YarnWeavingDispatchDetailUpdateSchema,
    YarnWeavingDispatchDetailWithEntryYarnHeavySchema,
)


class YarnWeavingDispatchBase(CustomBaseModel):
    exit_number: str | None = Field(
        validation_alias=AliasChoices("document_number", "entry_number")
    )
    period: int
    creation_date: date | None
    creation_time: str | None
    supplier_code: str | None = Field(
        default=None, validation_alias=AliasChoices("auxiliary_code", "supplier_code")
    )
    supplier_yarn_etry_number: str | None = Field(
        default=None,
        validation_alias="reference_number1",
    )
    service_order_id: str | None = Field(
        default=None, validation_alias="reference_number2"
    )
    document_note: str | None

    nrodir: str | None = Field(default=None, validation_alias="nrodir2")

    @field_serializer("creation_date", when_used="json")
    def serialize_creation_date(value: date | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

    class Config:
        from_attributes = True


class YarnWeavingDispatchSimpleSchema(YarnWeavingDispatchBase):
    pass


class YarnWeavingDispatchSimpleListSchema(CustomBaseModel):
    yarn_weaving_dispatches: list[YarnWeavingDispatchSimpleSchema] | None = []


class YarnWeavingDispatchFilterParams(CustomBaseModel):
    period: int | None = Field(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    )
    dispatch_number: str | None = Field(default=None)
    supplier_ids: list[str] | None = Field(default=None)
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    limit: int | None = Field(default=10, ge=1, le=100)
    offset: int | None = Field(default=0, ge=0)
    include_annulled: bool | None = Field(default=False)


class YarnWeavingDispatchSchema(YarnWeavingDispatchSimpleSchema):
    printed_flag: str | None
    status_flag: str | None = Field(exclude=True)
    promec_status: PromecStatusSchema | None = Field(default=None)

    @model_validator(mode="after")
    def set_promec_status(self):
        if self.status_flag is not None:
            self.promec_status = PromecStatusSchema(status_id=self.status_flag)
        return self

    detail: list[YarnWeavingDispatchDetailWithEntryYarnHeavySchema] | None = []


class YarnWeavingDispatchListSchema(CustomBaseModel):
    yarn_weaving_dispatches: list[YarnWeavingDispatchSchema] | None = []


class YarnWeavingDispatchPrintSchema(CustomBaseModel):
    dispatch_number: str


class YarnWeavingDispatchPrintListSchema(CustomBaseModel):
    dispatch_numbers: list[YarnWeavingDispatchPrintSchema] = []


class YarnWeavingDispatchCreateSchema(CustomBaseModel):
    supplier_code: str
    document_note: str | None = Field("", max_length=DOCUMENT_NOTE_MAX_LENGTH)
    nrodir: str | None = Field("000", max_length=NRODIR_MAX_LENGTH)
    service_order_id: str | None = Field(max_length=SERVICE_ORDER_ID_MAX_LENGTH)

    detail: list[YarnWeavingDispatchDetailCreateSchema] = Field(default=[])

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


class YarnWeavingDispatchUpdateSchema(CustomBaseModel):
    document_note: str | None = Field("", max_length=DOCUMENT_NOTE_MAX_LENGTH)
    nrodir: str | None = Field("000", max_length=NRODIR_MAX_LENGTH)

    detail: list[YarnWeavingDispatchDetailUpdateSchema] = Field(default=[])
