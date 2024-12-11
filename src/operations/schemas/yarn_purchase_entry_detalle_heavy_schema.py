
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
