from typing import Any

from pydantic import Field, computed_field, model_validator

from src.core.schemas import CustomBaseModel


class YarnPurchaseEntryDetailHeavyBase(CustomBaseModel):
    ingress_number: str | None = Field(default=None, exclude=True)
    item_number: int | None = Field(default=None, exclude=True)
    group_number: int | None = None
    status_flag: str | None = None
    cone_count: int | None = None
    package_count: int | None = None
    destination_storage: str | None = None
    net_weight: float | None = None
    gross_weight: float | None = None

    class Config:
        from_attributes = True


class YarnPurchaseEntryDetailHeavySimpleSchema(YarnPurchaseEntryDetailHeavyBase):
    exit_number: str | None = None
    dispatch_status: bool | None = None
    packages_left: int | None = None
    cones_left: int | None = None


class YarnPurchaseEntryDetailHeavySchema(YarnPurchaseEntryDetailHeavySimpleSchema):
    entry_user_id: str | None = Field(default=None)
    exit_user_id: str | None = Field(default=None)
    movement_detail: Any | None = Field(default=None, exclude=True)

    @computed_field
    @property
    def yarn_id(self) -> str | None:
        if self.movement_detail and hasattr(self.movement_detail, "product_code"):
            return self.movement_detail.product_code
        return None


class YarnPurchaseEntryDetailHeavyCreateSchema(CustomBaseModel):
    group_number: int | None = Field(default=0, ge=1)
    cone_count: int = Field(gt=0)
    package_count: int = Field(gt=0)
    gross_weight: float = Field(gt=0.0)
    net_weight: float | None = Field(default=0, gt=0.0)

    @model_validator(mode="after")
    def set_net_weight(self):
        if self.net_weight is None:
            self.net_weight = self.gross_weight

        return self


class YarnPurchaseEntryDetailHeavyUpdateSchema(
    YarnPurchaseEntryDetailHeavyCreateSchema
):
    pass
