from sqlmodel import SQLModel


class UsuarioBase(SQLModel):
    username: str
    email: str
    display_name: str


class UsuarioSimpleSchema(UsuarioBase):
    pass


class UsuarioSchema(UsuarioBase):
    roles: list["RolSimpleSchema"]
    accesos: list["AccesoSimpleSchema"]


class UsuarioCreateSchema(UsuarioBase):
    password: str
    rol_ids: list[int] | None = None
    acceso_ids: list[int] | None = None


class UsuarioUpdateSchema(SQLModel):
    display_name: str | None = None
    email: str | None = None


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
    roles: list[RolSimpleSchema]


class AccesoListSchema(SQLModel):
    data: list[AccesoSchema]
