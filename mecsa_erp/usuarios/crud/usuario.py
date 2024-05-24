from sqlmodel import SQLModel

from config.database import SessionDependency

from helpers.crud import CRUD

from mecsa_erp.usuarios.models import Usuario, UsuarioRol
from mecsa_erp.usuarios.schemas.usuario import UsuarioCreateSchema

crud_usuario = CRUD[Usuario, UsuarioCreateSchema](Usuario)
crud_usuario_rol = CRUD[UsuarioRol, UsuarioRol](UsuarioRol)


def validate_usuario_data(session: SessionDependency, usuario: SQLModel):
    user_exists = usuario.username and crud_usuario.get(
        session, Usuario.username == usuario.username
    )
    if user_exists:
        return False, f"Usuario {usuario.username} ya existe"

    email_exists = usuario.email and crud_usuario.get(
        session, Usuario.email == usuario.email
    )
    if email_exists:
        return False, f"Email {usuario.email} en uso"

    return True, None
