from pydantic import Field

from src.core.schemas import CustomBaseModel
from src.operations.constants import (
    CARD_ID_MAX_LENGTH,
)
from src.operations.models import CardOperation

from .card_operation_schema import (
    CardOperationSchema,
)


class DyeingServiceDispatchDetailBase(CustomBaseModel):
    net_weight: float | None = Field(default=None, validation_alias="guide_net_weight")
    roll_count: int | None = None
    fabric_id: str | None = Field(default=None, validation_alias="product_id")
    mecsa_weight: float | None = None

    class Config:
        from_attributes = True


class DyeingServiceDispatchDetailSchema(DyeingServiceDispatchDetailBase):
    tint_color_id: str | None = Field(exclude=True)
    meters_count: float | None = None
    detail_card: list[CardOperationSchema] | None = []


class DyeingServiceDispatchDetailsListSchema(CustomBaseModel):
    pass


class DyeingServiceDispatchDetailCreateSchema(CustomBaseModel):
    card_id: str = Field(max_length=CARD_ID_MAX_LENGTH)
    _card_operation: CardOperation


class DyeingServiceDispatchDetailUpdateSchema(DyeingServiceDispatchDetailCreateSchema):
    pass
