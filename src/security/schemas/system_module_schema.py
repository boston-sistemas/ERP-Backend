from pydantic import BaseModel, Field

from src.security.constants import (
    MAX_LENGTH_MODULO_IMAGE_PATH,
    MAX_LENGTH_MODULO_NOMBRE,
)


class SystemModuleBase(BaseModel):
    system_module_id: int = Field(validation_alias="id")
    name: str
    is_active: bool

    class Config:
        from_attributes = True


class SystemModuleSchema(SystemModuleBase):
    pass


class SystemModuleListSchema(BaseModel):
    system_modules: list[SystemModuleSchema]


class SystemModuleCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_LENGTH_MODULO_NOMBRE)
    image_path: str | None = Field(
        default=None, max_length=MAX_LENGTH_MODULO_IMAGE_PATH
    )
    is_active: bool = Field(default=True)


class SystemModuleFilterParams(BaseModel):
    include_inactive: bool = Field(default=False)
    limit: int | None = Field(default=10, ge=1, le=100)
    offset: int | None = Field(default=0, ge=0)
