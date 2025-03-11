from src.core.schemas import CustomBaseModel


class RateBase(CustomBaseModel):
    rate_id: int
    serial_code: str | None = None
    supplier_id: str | None = None
    fabric_id: str | None = None
    company_code: str | None = None
    currency: bool | None = None
    rate: float | None = None
    period: int | None = None
    month_number: int | None = None

    class Config:
        from_attributes = True


class RateSchema(RateBase):
    pass


class WeavingRateBase(RateSchema):
    pass


class WeavingRateSchema(WeavingRateBase):
    pass


class DyeingRateBase(RateSchema):
    color_id: str | None = None


class DyeingRateSchema(DyeingRateBase):
    pass
