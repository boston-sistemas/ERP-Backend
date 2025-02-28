from pydantic import Field, model_validator

from src.core.schemas import CustomBaseModel

STATUS = {"P": "Pendiente", "A": "Anulado", "C": "Cerrado"}


class PromecStatusBase(CustomBaseModel):
    status_id: str | None = Field(validation_alias="status_flag")
    name: str | None = None

    class Config:
        from_attributes = True


class PromecStatusSchema(PromecStatusBase):
    @model_validator(mode="after")
    def set_name(self):
        if self.status_id:
            if STATUS.get(self.status_id):
                self.name = STATUS.get(self.status_id)

        return self


CURRENCY = {
    1: {"symbol": "S/.", "name": "Soles"},
    2: {"symbol": "$/.", "name": "Dólares"},
}


class PromecCurrencyBase(CustomBaseModel):
    currency_id: int | None = Field(validation_alias="currency_code")
    symbol: str | None = None
    name: str | None = None

    class Config:
        from_attributes = True


class PromecCurrencySchema(PromecCurrencyBase):
    @model_validator(mode="after")
    def set_name(self):
        if self.currency_id:
            if CURRENCY.get(self.currency_id):
                if CURRENCY.get(self.currency_id).get("symbol"):
                    self.symbol = CURRENCY.get(self.currency_id).get("symbol")
                if CURRENCY.get(self.currency_id).get("name"):
                    self.name = CURRENCY.get(self.currency_id).get("name")

        return self
