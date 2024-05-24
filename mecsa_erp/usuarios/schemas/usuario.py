from sqlmodel import Field, SQLModel
from pydantic import EmailStr


class UsuarioBase(SQLModel):
    username: str = Field(min_length=1)
    email: EmailStr
    display_name: str | None = None


class UsuarioSimpleSchema(UsuarioBase):
    pass


class UsuarioSchema(UsuarioBase):
    roles: list["RolSimpleSchema"]


class UsuarioCreateSchema(UsuarioBase):
    password: str
    rol_ids: list[int] | None = None


class UsuarioUpdateSchema(SQLModel):
    username: str = Field(default=None, min_length=1)
    display_name: str | None = None
    email: EmailStr | None = None


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
