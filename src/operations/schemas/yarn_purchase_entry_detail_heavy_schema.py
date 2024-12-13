from pydantic import Field, root_validator

from src.core.schemas import CustomBaseModel


class YarnPurchaseEntryDetalleHeavyBase(CustomBaseModel):
    group_number: int
    status_flag: str | None
    cone_count: int | None
    package_count: int | None
    destination_storage: str | None
    net_weight: float | None
    gross_weight: float | None


class YarnPurchaseEntryDetalleHeavySimpleSchema(YarnPurchaseEntryDetalleHeavyBase):
    exit_number: str | None
    dispatch_status: bool | None
    packages_left: int | None


class YarnPurchaseEntryDetalleHeavySchema(YarnPurchaseEntryDetalleHeavySimpleSchema):
    entry_user_id: str | None
    exit_user_id: str | None


class YarnPurchaseEntryDetalleHeavyCreateSchema(CustomBaseModel):
    group_number: int | None = Field(default=0, ge=1)
    cone_count: int = Field(gt=0)
    package_count: int = Field(gt=0)
    gross_weight: float = Field(gt=0.0)
    net_weight: float | None = Field(default=0, gt=0.0)

    @root_validator(pre=True)
    def set_net_weight(cls, values):
        if values.get("net_weight") is None:
            values["net_weight"] = values["gross_weight"]
        return values

