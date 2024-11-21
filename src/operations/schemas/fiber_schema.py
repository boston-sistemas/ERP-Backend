from src.core.schemas import CustomBaseModel
from src.security.schemas import ParameterValueSchema

from .mecsa_color_schema import MecsaColorSchema


class FiberBase(CustomBaseModel):
    id: str
    category_id: int
    denomination: str | None
    origin: str | None
    color_id: str | None

    class Config:
        from_attributes = True


class FiberSchema(FiberBase):
    pass


class FiberCompleteSchema(FiberSchema):
    category: ParameterValueSchema
    color: MecsaColorSchema | None = None


class FiberCompleteListSchema(CustomBaseModel):
    fibers: list[FiberCompleteSchema]
