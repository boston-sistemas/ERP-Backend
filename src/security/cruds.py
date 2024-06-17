from core.crud import CRUD
from core.database import SessionDependency
from sqlmodel import SQLModel

from security.models import Acceso, Rol, RolAcceso, Sesion, Usuario, UsuarioRol
from security.schemas import RolCreateSchema, UsuarioCreateSchema

crud_sesion = CRUD[Sesion, Sesion](Sesion)

crud_usuario = CRUD[Usuario, UsuarioCreateSchema](Usuario)

crud_usuario_rol = CRUD[UsuarioRol, UsuarioRol](UsuarioRol)

crud_acceso = CRUD[Acceso, Acceso](Acceso)

crud_rol = CRUD[Rol, RolCreateSchema](Rol)

crud_rol_acceso = CRUD[RolAcceso, RolAcceso](RolAcceso)


def validate_usuario_data(session: SessionDependency, usuario: SQLModel):
    username_exists = usuario.username and crud_usuario.get(
        session, Usuario.username == usuario.username
    )
    if username_exists:
        return False, f"Usuario {usuario.username} ya existe"

    return True, None
