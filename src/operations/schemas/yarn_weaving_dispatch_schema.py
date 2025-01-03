from datetime import date

from pydantic import AliasChoices, Field, model_validator

from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    DOCUMENT_NOTE_MAX_LENGTH,
    NRODIR_MAX_LENGTH,
    SERVICE_ORDER_ID_MAX_LENGTH,
)

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
    status_flag: str | None
    document_note: str | None

    nrodir: str | None = Field(default=None, validation_alias="nrodir2")

    class Config:
        from_attributes = True


class YarnWeavingDispatchSimpleSchema(YarnWeavingDispatchBase):
    pass


class YarnWeavingDispatchSimpleListSchema(CustomBaseModel):
    yarn_weaving_dispatches: list[YarnWeavingDispatchSimpleSchema] | None = []


class YarnWeavingDispatchSchema(YarnWeavingDispatchSimpleSchema):
    printed_flag: str | None
    detail: list[YarnWeavingDispatchDetailWithEntryYarnHeavySchema] | None = []


class YarnWeavingDispatchCreateSchema(CustomBaseModel):
    period: int
    supplier_code: str
    document_note: str | None = Field(None, max_length=DOCUMENT_NOTE_MAX_LENGTH)
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
    supplier_code: str
    document_note: str | None = Field(None, max_length=DOCUMENT_NOTE_MAX_LENGTH)
    nrodir: str | None = Field("000", max_length=NRODIR_MAX_LENGTH)

    detail: list[YarnWeavingDispatchDetailUpdateSchema] = Field(default=[])

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
