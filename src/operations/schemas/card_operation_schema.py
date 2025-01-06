from pydantic import Field

from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    CARD_TYPE_MAX_LENGTH,
    COLOR_ID_MAX_LENGTH,
    FABRIC_ID_MAX_LENGTH,
    SUPPLIER_CODE_MAX_LENGTH,
)


class CardOperationBase(CustomBaseModel):
    id: str | None = None
    fabric_id: str | None
    net_weight: float | None
    tint_supplier_id: str | None
    tint_color_id: str | None
    yarn_supplier_id: str | None
    card_type: str | None
    status_flag: str | None

    class Config:
        from_attributes = True


class CardOperationSimpleSchema(CardOperationBase):
    pass


class CardOperationSchema(CardOperationSimpleSchema):
    pass


class CardOperationCreateSchema(CustomBaseModel):
    fabric_id: str = Field(max_length=FABRIC_ID_MAX_LENGTH)
    net_weight: float
    tint_supplier_id: str = Field(max_length=SUPPLIER_CODE_MAX_LENGTH)
    tint_color_id: str = Field(max_length=COLOR_ID_MAX_LENGTH)
    yarn_supplier_id: str = Field(max_length=SUPPLIER_CODE_MAX_LENGTH)
    card_type: str = Field(max_length=CARD_TYPE_MAX_LENGTH)


class CardOperationUpdateSchema(CardOperationCreateSchema):
    pass
