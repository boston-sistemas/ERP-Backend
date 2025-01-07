from datetime import date

from pydantic import Field, model_validator

from src.core.schemas import CustomBaseModel

class DyeingServiceDispatchDetailCardBase(CustomBaseModel):

    class Config:
        from_attributes = True

class DyeingServiceDispatchDetailCardSchema(DyeingServiceDispatchDetailCardBase):
    pass

class DyeingServiceDispatchDetailCardsListSchema(CustomBaseModel):
    pass

class DyeingServiceDispatchDetailCardCreateSchema(CustomBaseModel):
    pass

class DyeingServiceDispatchDetailCardUpdateSchema(CustomBaseModel):
    pass
