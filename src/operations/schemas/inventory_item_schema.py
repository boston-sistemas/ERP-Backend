from pydantic import field_validator

from src.core.schemas import CustomBaseModel
from src.core.utils import is_active_status


class InventoryItemBase(CustomBaseModel):
    id: str
    inventory_unit_code: str | None
    purchase_unit_code: str | None
    description: str | None
    purchase_description: str | None
    barcode: int | None
    is_active: bool

    @field_validator("is_active", mode="before")
    def convert_is_active(cls, value):
        return is_active_status(value)


class InventoryItemSimpleSchema(InventoryItemBase):
    class Config:
        from_attributes = True
