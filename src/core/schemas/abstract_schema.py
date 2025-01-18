from typing import Any

from pydantic import Field, model_validator

from .custom_schema import CustomBaseModel


class ItemIsUpdatableSchema(CustomBaseModel):
    updatable: bool = Field(
        default=False, description="Indica si el objeto puede ser actualizado."
    )
    is_partial: bool = Field(
        default=False,
        description="Indica si la actualización es parcial (True) o completa (False).",
    )
    message: str = Field(
        default="La actualización es posible.",
        description="Mensaje informativo. Si la actualización no es posible, indica el motivo.",
    )
    fields: list[str] = Field(
        default=[],
        description="Lista de campos que pueden ser actualizados en caso de una actualización parcial.",
        example=["field1", "field2", "field3"],
    )

    failure: Any | None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def set_fields(self):
        failure = self.failure
        self.updatable = True if self.is_partial or not failure else False
        self.message = (
            failure.error.detail if not self.updatable and failure else self.message
        )

        return self


class ItemStatusUpdateSchema(CustomBaseModel):
    is_active: bool = Field(
        description="Establezca en `True` para activar, `False` para desactivar."
    )
