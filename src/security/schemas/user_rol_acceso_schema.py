from datetime import datetime

from pydantic import BaseModel, EmailStr
from sqlmodel import Field


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
    blocked_until: datetime | None
    roles: list["RolSimpleSchema"]

    class Config:
        from_attributes = True


class UsuarioCreateSchema(UsuarioBase):
    password: str = Field(min_length=1)


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


#######################################################


class RolBase(BaseModel):
    nombre: str = Field(min_length=1)
    is_active: bool = Field(default=True)


class RolCreateSchema(RolBase):
    pass


class RolCreateWithAccesosSchema(RolCreateSchema):
    acceso_ids: list[int] | None = None


class RolUpdateSchema(BaseModel):
    nombre: str = Field(default=None, min_length=1)
    is_active: bool | None = None


class RolSimpleSchema(RolBase):
    class Config:
        from_attributes = True


class RolSchema(RolBase):
    rol_id: int
    accesos: list["AccesoSimpleSchema"]

    class Config:
        from_attributes = True


class RolListSchema(BaseModel):
    roles: list[RolSchema]


#######################################################


class AccesoBase(BaseModel):
    acceso_id: int
    nombre: str
    is_active: bool


class AccesoSimpleSchema(AccesoBase):
    class Config:
        from_attributes = True


class AccesoSchema(AccesoBase):
    roles: list[RolSimpleSchema]


class AccesoListSchema(BaseModel):
    accesos: list[AccesoSimpleSchema]
