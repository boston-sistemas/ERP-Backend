from datetime import date
from typing import Any

from pydantic import AliasChoices, Field, computed_field, model_validator

from src.core.schemas import CustomBaseModel
from src.operations.constants import PRODUCT_CODE_MAX_LENGTH

class CardOperationBase(CustomBaseModel):

    id: str | None = None
    fabric_id: str | None
    net_weight: float | None
    tint_supplier_id: str | None
    tint_color_id: str | None
    yarn_supplier_id: str | None
    card_type: str | None

    class Config:
        from_attributes = True

class CardOperationSimpleSchema(CardOperationBase):

    pass

class CardOperationSchema(CardOperationSimpleSchema):

    pass
