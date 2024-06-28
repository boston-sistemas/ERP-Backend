from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel


class UsuarioBase(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    display_name: str


class UsuarioSimpleSchema(UsuarioBase):
    pass


class UsuarioSchema(UsuarioBase):
    usuario_id: int
    is_active: bool
    blocked_until: datetime | None
    roles: list["RolSimpleSchema"]

    class Config:
        from_attributes = True


class UsuarioCreateSchema(UsuarioBase):
    password: str = Field(min_length=1)
    rol_ids: list[int] | None = None


class UsuarioUpdateSchema(UsuarioBase):
    pass


class UsuarioListSchema(SQLModel):
    usuarios: list[UsuarioSchema]


#######################################################


class RolBase(BaseModel):
    nombre: str = Field(min_length=1)
    is_active: bool = Field(default=True)


class RolCreateSchema(RolBase):
    acceso_ids: Optional[List[int]] = None


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
    roles: List[RolSimpleSchema]


class AccesoListSchema(BaseModel):
    accesos: List[AccesoSimpleSchema]
