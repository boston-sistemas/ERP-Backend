from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator

from src.security.constants import (
    MAX_LENGTH_ACCESO_DESCRIPTION,
    MAX_LENGTH_ACCESO_IMAGE_PATH,
    MAX_LENGTH_ACCESO_NOMBRE,
    MAX_LENGTH_ACCESO_SCOPE,
    MAX_LENGTH_ACCESO_VIEW_PATH,
)

from .operation_schema import OperationSchema


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
    rol_id: int = Field(validation_alias="rol_id")
    nombre: str = Field(min_length=1)
    is_active: bool = Field(default=True)
    rol_color: str

    class Config:
        from_attributes = True


class RolSimpleSchema(RolBase):
    pass


class RolAccesoOperationSchema(BaseModel):
    rol_id: int
    operation_id: int
    acceso_id: int
    acceso: "AccesoSchema" = None
    operation: "OperationSchema" = None
    rol: "RolSchema" = None

    class Config:
        from_attributes = True


class RolSchema(RolBase):
    access_operation: list[RolAccesoOperationSchema] = Field(default=[], exclude=True)
    access: list["AccesoSchema"] = []

    @model_validator(mode="after")
    def set_access(self):
        for rao in self.access_operation:
            if rao.rol_id == self.rol_id:
                if rao.acceso_id not in [a.acceso_id for a in self.access]:
                    rao.acceso.operations.append(rao.operation)
                    self.access.append(rao.acceso)
                else:
                    for a in self.access:
                        if a.acceso_id == rao.acceso.acceso_id:
                            if rao.operation.operation_id not in [
                                op.operation_id for op in a.operations
                            ]:
                                a.operations.append(rao.operation)

        return self


class RolCreateSchema(BaseModel):
    nombre: str = Field(min_length=1)
    is_active: bool = Field(default=True)
    rol_color: str


class AccesoCreateWithOperationSchema(BaseModel):
    acceso_id: int
    operation_ids: list[int]


class RolCreateAccessWithOperationSchema(BaseModel):
    accesses: list[AccesoCreateWithOperationSchema] = []


class AccesoDeleteWithOperationSchema(BaseModel):
    acceso_id: int
    operation_ids: list[int]


class RolDeleteAccessWithOperationSchema(BaseModel):
    accesses: list[AccesoDeleteWithOperationSchema] = []


class RolCreateWithAccesosSchema(RolCreateSchema):
    accesses: list[AccesoCreateWithOperationSchema]


class RolUpdateSchema(BaseModel):
    nombre: str = Field(default=None, min_length=1)
    is_active: bool | None = None
    rol_color: str | None = None


class RolListSchema(BaseModel):
    roles: list[RolSchema]


#######################################################


class AccesoBase(BaseModel):
    acceso_id: int = Field(validation_alias="acceso_id")
    nombre: str
    is_active: bool | None = None

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
    operations: list[OperationSchema] = []
    # roles: list[RolSimpleSchema] = []


class AccesoListSchema(BaseModel):
    accesos: list[AccesoSimpleSchema]
