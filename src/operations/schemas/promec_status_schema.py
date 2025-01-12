from src.core.schemas import CustomBaseModel

from pydantic import Field, model_validator

class PromecStatusBase(CustomBaseModel):
    status_id: str | None = Field(
        validation_alias="status_flag"
    )
    name: str | None = None

    class Config:
        from_attributes = True

class PromecStatusSchema(PromecStatusBase):

    @model_validator(mode="after")
    def set_name(self):
        if self.status_id:
            if self.status_id == "P":
                self.name = "Pendiente"
            elif self.status_id == "A":
                self.name = "Anulado"
            elif self.status_id == "C":
                self.name = "Cerrado"

        return self


