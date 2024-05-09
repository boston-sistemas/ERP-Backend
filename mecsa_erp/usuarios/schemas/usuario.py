from sqlmodel import SQLModel


class UsuarioBase(SQLModel):
    username: str
    email: str
    display_name: str


class UsuarioSchema(UsuarioBase):
    pass


class UsuarioCreateSchema(UsuarioBase):
    password: str


class UsuarioListSchema(SQLModel):
    data: list[UsuarioSchema]


#######################################################


class RolBase(SQLModel):
    rol_id: int
    nombre: str


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


class AccesoSimpleSchema(AccesoBase):
    pass


class AccesoSchema(AccesoBase):
    rol: RolSimpleSchema


class AccesoListSchema(SQLModel):
    data: list[AccesoSchema]
