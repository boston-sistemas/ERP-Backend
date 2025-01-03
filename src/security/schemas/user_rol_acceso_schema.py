from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


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


class AccesoSimpleSchema(AccesoBase):
    class Config:
        from_attributes = True


class AccesoSchema(AccesoBase):
    roles: list[RolSimpleSchema]


class AccesoListSchema(BaseModel):
    accesos: list[AccesoSimpleSchema]
