from datetime import date

from pydantic import Field, computed_field, model_validator

from src.core.constants import PAGE_SIZE
from src.core.schemas import CustomBaseModel
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    CODE_MAX_LENGTH,
    FABRIC_ID_MAX_LENGTH,
    SERIAL_NUMBER_MAX_LENGTH,
    SUPPLIER_CODE_MAX_LENGTH,
)

CURRENCY_NAMES = {0: "Dólares", 1: "Soles"}


class RateBase(CustomBaseModel):
    rate_id: int
    serial_code: str | None = None
    supplier_id: str | None = None
    fabric_id: str | None = None
    currency: bool | None = Field(exclude=True)
    rate: float | None = None
    period: int | None = None
    month_number: int | None = None

    class Config:
        from_attributes = True


class RateSchema(RateBase):
    currency_name: str | None = None

    @model_validator(mode="after")
    def set_currency_name(self):
        if self.currency is not None:
            self.currency_name = CURRENCY_NAMES.get(int(self.currency))

        return self


class RateCreateSchema(CustomBaseModel):
    serial_code: str = Field(min_length=1, max_length=SERIAL_NUMBER_MAX_LENGTH)
    supplier_id: str = Field(min_length=1, max_length=SUPPLIER_CODE_MAX_LENGTH)
    fabric_id: str = Field(min_length=1, max_length=FABRIC_ID_MAX_LENGTH)
    currency: bool = Field(default=False)
    rate: float = Field(gt=0)
    extended_rate: float = Field(default=0.0, ge=0)
    project_rate: float = Field(default=0.0, ge=0)
    code: str | None = Field(default="", min_length=1, max_length=CODE_MAX_LENGTH)

    @computed_field
    def period(self) -> int:
        return calculate_time(tz=PERU_TIMEZONE).date().year

    @computed_field
    def month_number(self) -> int:
        return calculate_time(tz=PERU_TIMEZONE).date().month


class RateListSchema(CustomBaseModel):
    service_rates: list[RateSchema] | None = []


class RateUpdateSchema(CustomBaseModel):
    rate: float = Field(gt=0)
    extended_rate: float = Field(default=0.0, ge=0)
    project_rate: float = Field(default=0.0, ge=0)


class WeavingRateBase(RateSchema):
    pass


class WeavingRateSchema(WeavingRateBase):
    pass


class DyeingRateBase(RateSchema):
    color_id: str | None = None


class DyeingRateSchema(DyeingRateBase):
    pass


class RateFilterParams(CustomBaseModel):
    period: int | None = Field(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    )
    month_number: int | None = Field(
        default=calculate_time(tz=PERU_TIMEZONE).date().month,
    )
    serial_code: str | None = Field(default=None)
    supplier_ids: list[str] | None = Field(default=None)
    fabric_ids: list[str] | None = Field(default=None)
    currency: bool | None = Field(default=None)
    page: int | None = Field(default=1, ge=1)

    @computed_field
    def limit(self) -> int:
        return PAGE_SIZE

    @computed_field
    def offset(self) -> int:
        return (self.page - 1) * PAGE_SIZE
