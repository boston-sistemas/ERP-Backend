from datetime import date

from pydantic import Field, model_validator

from src.core.schemas import CustomBaseModel

from .dyeing_service_dispatch_detail_card_schema import (
    DyeingServiceDispatchDetailCardCreateSchema,
    DyeingServiceDispatchDetailCardSchema,
    DyeingServiceDispatchDetailCardUpdateSchema,
)

class DyeingServiceDispatchDetailBase(CustomBaseModel):

    net_weight: float | None = Field(
        default=None, validation_alias="guide_net_weight"
    )
    roll_count: int | None = None
    fabric_id: str | None = Field(
        default=None, validation_alias="product_id"
    )
    mecsa_weight: float | None = None

    class Config:
        from_attributes = True

class DyeingServiceDispatchDetailSchema(DyeingServiceDispatchDetailBase):
    detail_card: list[DyeingServiceDispatchDetailCardSchema] | None = []

class DyeingServiceDispatchDetailsListSchema(CustomBaseModel):
    pass

class DyeingServiceDispatchDetailCreateSchema(CustomBaseModel):
    pass

class DyeingServiceDispatchDetailUpdateSchema(CustomBaseModel):
    pass
