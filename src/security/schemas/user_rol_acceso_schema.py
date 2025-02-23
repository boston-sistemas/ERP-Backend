from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.security.constants import (
    MAX_LENGTH_ACCESO_DESCRIPTION,
    MAX_LENGTH_ACCESO_IMAGE_PATH,
    MAX_LENGTH_ACCESO_NOMBRE,
    MAX_LENGTH_ACCESO_SCOPE,
    MAX_LENGTH_ACCESO_VIEW_PATH,
)


class UsuarioBase(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    display_name: str


class UsuarioSimpleSchema(UsuarioBase):
    class Config:
        from_attributes = True


class UsuarioSchema(UsuarioBase):
    usuario_id: int
    is_active: bool
    reset_password_at: datetime
    blocked_until: datetime | None
    roles: list["RolSimpleSchema"]

    class Config:
        from_attributes = True


class UsuarioCreateSchema(UsuarioBase):
    pass


class UsuarioCreateWithRolesSchema(UsuarioCreateSchema):
    rol_ids: list[int] | None = None


class UsuarioUpdateSchema(BaseModel):
    username: str = Field(default=None, min_length=1)
    email: EmailStr | None = None
    display_name: str | None = None
    is_active: bool | None = None
    blocked_until: datetime | None = None


class UsuarioListSchema(BaseModel):
    usuarios: list[UsuarioSchema]


class UsuarioUpdatePasswordSchema(BaseModel):
    new_password: str


#######################################################


class RolBase(BaseModel):
    rol_id: int
    nombre: str = Field(min_length=1)
    is_active: bool = Field(default=True)
    rol_color: str

    class Config:
        from_attributes = True


class RolSimpleSchema(RolBase):
    pass


class RolSchema(RolBase):
    rol_id: int
    accesos: list["AccesoSimpleSchema"]


class RolCreateSchema(BaseModel):
    nombre: str = Field(min_length=1)
    is_active: bool = Field(default=True)
    rol_color: str


class RolCreateWithAccesosSchema(RolCreateSchema):
    acceso_ids: list[int] | None = None


class RolUpdateSchema(BaseModel):
    nombre: str = Field(default=None, min_length=1)
    is_active: bool | None = None
    rol_color: str | None = None


class RolListSchema(BaseModel):
    roles: list[RolSchema]


#######################################################


class AccesoBase(BaseModel):
    acceso_id: int
    nombre: str
    is_active: bool

    class Config:
        from_attributes = True


class AccesoSimpleSchema(AccesoBase):
    pass


class AccessCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_LENGTH_ACCESO_NOMBRE)
    scope: str = Field(min_length=1, max_length=MAX_LENGTH_ACCESO_SCOPE)
    system_module_id: int
    view_path: str = Field(min_length=1, max_length=MAX_LENGTH_ACCESO_VIEW_PATH)
    image_path: str | None = Field(
        None, min_length=1, max_length=MAX_LENGTH_ACCESO_IMAGE_PATH
    )
    description: str | None = Field("", max_length=MAX_LENGTH_ACCESO_DESCRIPTION)
    is_active: bool = Field(default=True)


class AccesoSchema(AccesoBase):
    roles: list[RolSimpleSchema] = []


class AccesoListSchema(BaseModel):
    accesos: list[AccesoSimpleSchema]
