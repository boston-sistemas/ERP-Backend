from datetime import datetime
from sqlmodel import Field, SQLModel
from pydantic import EmailStr


class UsuarioBase(SQLModel):
    username: str = Field(min_length=1)
    email: EmailStr
    display_name: str | None = None
    is_active: bool = Field(default=True)
    blocked_until: datetime | None = None


class UsuarioSimpleSchema(UsuarioBase):
    pass


class UsuarioSchema(UsuarioBase):
    roles: list["RolSimpleSchema"]


class UsuarioCreateSchema(UsuarioBase):
    password: str
    rol_ids: list[int] | None = None


class UsuarioUpdateSchema(SQLModel):
    username: str = Field(default=None, min_length=1)
    email: EmailStr | None = None
    display_name: str | None = None
    is_active: bool | None = None
    blocked_until: datetime | None = None


class UsuarioListSchema(SQLModel):
    data: list[UsuarioSchema]


#######################################################


class RolBase(SQLModel):
    rol_id: int
    nombre: str
    is_active: bool


class RolSimpleSchema(RolBase):
    pass


class RolSchema(RolBase):
    accesos: list["AccesoSimpleSchema"]


class RolCreateSchema(SQLModel):
    nombre: str = Field(min_length=1)
    is_active: bool = Field(default=True)
    acceso_ids: list[int] | None = None


class RolUpdateSchema(SQLModel):
    nombre: str = Field(default=None, min_length=1)
    is_active: bool | None = None


class RolListSchema(SQLModel):
    data: list[RolSchema]


#######################################################


class AccesoBase(SQLModel):
    acceso_id: int
    nombre: str
    is_active: bool


class AccesoSimpleSchema(AccesoBase):
    pass


class AccesoSchema(AccesoBase):
    roles: list[RolSimpleSchema]


class AccesoListSchema(SQLModel):
    data: list[AccesoSchema]
