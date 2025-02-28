from datetime import date
from typing import Any

from pydantic import AliasChoices, Field, computed_field, model_validator

from src.core.schemas import CustomBaseModel
from src.operations.constants import PRODUCT_CODE_MAX_LENGTH

from .yarn_purchase_entry_detail_heavy_schema import (
    YarnPurchaseEntryDetailHeavyCreateSchema,
    YarnPurchaseEntryDetailHeavySimpleSchema,
    YarnPurchaseEntryDetailHeavyUpdateSchema,
)


class YarnPurchaseEntryDetailBase(CustomBaseModel):
    item_number: int | None
    yarn_id: str | None = Field(
        validation_alias=AliasChoices("product_code1", "yarn_id"),
    )
    mecsa_weight: float | None
    status_flag: str | None
    is_weighted: bool | None

    class Config:
        from_attributes = True


class YarnPurchaseEntryDetailSimpleSchema(YarnPurchaseEntryDetailBase):
    guide_gross_weight: float | None
    detail_aux: Any = Field(default=None, exclude=True)
    detail_heavy: list[YarnPurchaseEntryDetailHeavySimpleSchema]
    supplier_batch: str | None = (Field(default=None),)

    @computed_field
    @property
    def guide_net_weight(self) -> float | None:
        if self.detail_aux and hasattr(self.detail_aux, "guide_net_weight"):
            return self.detail_aux.guide_net_weight
        return None

    @computed_field
    @property
    def guide_cone_count(self) -> int | None:
        if self.detail_aux and hasattr(self.detail_aux, "guide_cone_count"):
            return self.detail_aux.guide_cone_count
        return None

    @computed_field
    @property
    def guide_package_count(self) -> int | None:
        if self.detail_aux and hasattr(self.detail_aux, "guide_package_count"):
            return self.detail_aux.guide_package_count
        return None


class YarnPurchaseEntryDetaileSchema(YarnPurchaseEntryDetailSimpleSchema):
    creation_date: date | None
    creation_time: str | None
    precto: float | None
    impcto: float | None
    impmn1: float | None
    impmn2: float | None
    ctomn1: float | None
    ctomn2: float | None

    @computed_field
    @property
    def reference_code(self) -> str | None:
        if self.detail_aux and hasattr(self.detail_aux, "reference_code"):
            return self.detail_aux.reference_code
        return None


class YarnPurchaseEntryDetailListSchema(CustomBaseModel):
    yarn_purchase_entry_detalles: list[YarnPurchaseEntryDetailBase] = []


class YarnPurchaseEntryDetailCreateSchema(CustomBaseModel):
    item_number: int | None = Field(default=None, ge=1)
    yarn_id: str = Field(min_length=1, max_length=PRODUCT_CODE_MAX_LENGTH)
    guide_net_weight: float = Field(gt=0.0)
    guide_gross_weight: float = Field(gt=0.0)
    guide_cone_count: int = Field(gt=0)
    guide_package_count: int = Field(gt=0)

    detail_heavy: list[YarnPurchaseEntryDetailHeavyCreateSchema] = Field(default=[])

    is_weighted: bool = Field(default=False)

    @computed_field
    @property
    def mecsa_weight(self) -> float:
        return sum(heavy.net_weight for heavy in self.detail_heavy)

    @model_validator(mode="after")
    def initialize_detail_heavy(self):
        if not self.detail_heavy and not self.is_weighted:
            self.detail_heavy = [
                YarnPurchaseEntryDetailHeavyCreateSchema(
                    group_number=1,
                    net_weight=self.guide_net_weight,
                    gross_weight=self.guide_gross_weight,
                    cone_count=self.guide_cone_count,
                    package_count=self.guide_package_count,
                )
            ]
        elif self.detail_heavy:
            self.is_weighted = True
        return self

    @model_validator(mode="after")
    def align_group_numbers(self):
        total = len(self.detail_heavy)
        assigned_nums = [
            d.group_number for d in self.detail_heavy if d.group_number is not None
        ]

        if len(assigned_nums) != len(set(assigned_nums)) or any(
            num < 1 or num > total for num in assigned_nums
        ):
            for i, d in enumerate(self.detail_heavy, start=1):
                d.group_number = i
            return self

        used = set(assigned_nums)
        missing = [i for i in range(1, total + 1) if i not in used]

        m_idx = 0
        for d in self.detail_heavy:
            if d.group_number is None:
                d.group_number = missing[m_idx]
                m_idx += i

        return self


class YarnPurchaseEntryDetailUpdateSchema(YarnPurchaseEntryDetailCreateSchema):
    item_number: int = Field(ge=1)
    detail_heavy: list[YarnPurchaseEntryDetailHeavyUpdateSchema] = Field(default=[])
    is_weighted: bool = Field(default=False, exclude=True)

    @model_validator(mode="after")
    def initialize_detail_heavy(self):
        if not self.detail_heavy:
            self.is_weighted = False
            self.detail_heavy = [
                YarnPurchaseEntryDetailHeavyUpdateSchema(
                    group_number=1,
                    net_weight=self.guide_net_weight,
                    gross_weight=self.guide_gross_weight,
                    cone_count=self.guide_cone_count,
                    package_count=self.guide_package_count,
                )
            ]
        else:
            self.is_weighted = True
        return self
