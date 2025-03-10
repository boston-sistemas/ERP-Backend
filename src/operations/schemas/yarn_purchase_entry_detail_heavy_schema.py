from typing import Any

from pydantic import Field, computed_field, field_serializer, model_validator

from src.core.schemas import CustomBaseModel


class YarnPurchaseEntryDetailHeavyBase(CustomBaseModel):
    ingress_number: str | None = Field(default=None)  # , exclude=True)
    item_number: int | None = Field(default=None)  # , exclude=True)
    group_number: int | None = None
    period: int | None = None
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
    supplier_batch: str | None = (Field(default=None),)


class YarnPurchaseEntryDetailHeavySchema(YarnPurchaseEntryDetailHeavySimpleSchema):
    entry_user_id: str | None = Field(default=None)
    exit_user_id: str | None = Field(default=None)
    movement_detail: Any | None = Field(default=None, exclude=True)
    supplier_yarn_id: str | None = Field(default=None)
    yarn_id: str | None = Field(default=None)

    unit_net_weight_for_cone: float | None = Field(default=None)
    unit_net_weight_for_package: float | None = Field(default=None)

    unit_gross_weight_for_cone: float | None = Field(default=None)
    unit_gross_weight_for_package: float | None = Field(default=None)

    gross_weight_left: float | None = Field(default=None)
    net_weight_left: float | None = Field(default=None)

    @model_validator(mode="after")
    def set_units_weights(self):
        if self.net_weight is not None:
            self.unit_net_weight_for_cone = self.net_weight / self.cone_count
            self.unit_net_weight_for_package = self.net_weight / self.package_count

        if self.gross_weight is not None:
            self.unit_gross_weight_for_cone = self.gross_weight / self.cone_count
            self.unit_gross_weight_for_package = self.gross_weight / self.package_count

        return self

    @model_validator(mode="after")
    def set_weights_left(self):
        if self.net_weight and self.packages_left and self.package_count:
            if self.packages_left == self.package_count:
                self.net_weight_left = self.net_weight
            else:
                self.net_weight_left = self.unit_net_weight_for_package * (
                    self.package_count - self.packages_left
                )
        else:
            self.net_weight_left = self.net_weight

        if self.gross_weight and self.package_count and self.packages_left:
            if self.packages_left == self.package_count:
                self.gross_weight_left = self.gross_weight
            else:
                self.gross_weight_left = self.unit_gross_weight_for_package * (
                    self.package_count - self.packages_left
                )
        else:
            self.gross_weight_left = self.gross_weight

        return self


class YarnPurchaseEntryAvailabilitySchema(CustomBaseModel):
    entry_number: str | None = Field(default=None)
    detail_heavy: list[YarnPurchaseEntryDetailHeavySchema] = []

    @field_serializer("detail_heavy")
    def sort_detail_heavy(self, value):
        return (
            sorted(
                value,
                key=lambda x: (
                    x.ingress_number or "",
                    x.item_number or 0,
                    x.group_number or 0,
                ),
            )
            if value
            else value
        )


class YarnPurchaseEntryDetailHeavyListSchema(CustomBaseModel):
    yarn_purchase_entries_detail_heavy: list[YarnPurchaseEntryDetailHeavySchema] = (
        Field(
            default=[],
            exclude=True,
        )
    )

    yarn_purchase_entries: list[YarnPurchaseEntryAvailabilitySchema] = []

    @model_validator(mode="after")
    def set_yarn_purchase_entries(self):
        for heavy in self.yarn_purchase_entries_detail_heavy:
            if heavy.ingress_number not in [
                entry.entry_number for entry in self.yarn_purchase_entries
            ]:
                self.yarn_purchase_entries.append(
                    YarnPurchaseEntryAvailabilitySchema(
                        entry_number=heavy.ingress_number, detail_heavy=[heavy]
                    )
                )
            else:
                for entry in self.yarn_purchase_entries:
                    if entry.entry_number == heavy.ingress_number:
                        if heavy not in entry.detail_heavy:
                            entry.detail_heavy.append(heavy)
        return self


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
    group_number: int = Field(ge=1)
