from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import joinedload

from config.database import SessionDependency
from helpers.crud import CRUD

from mecsa_erp.usuarios.api.acceso import crud_acceso
from mecsa_erp.usuarios.api.rol import crud_rol

from mecsa_erp.usuarios.models import Usuario

from mecsa_erp.usuarios.schemas.usuario import (
    UsuarioCreateSchema,
    UsuarioListSchema,
    UsuarioSchema,
    UsuarioUpdateSchema,
)

from mecsa_erp.usuarios.security import get_password_hash

crud_usuario = CRUD[Usuario, UsuarioCreateSchema](Usuario)

router = APIRouter(tags=["Usuarios"], prefix="/usuarios")


@router.get("/{username}", response_model=UsuarioSchema)
def get_usuario(session: SessionDependency, username: str):
    usuario = crud_usuario.get_by_pk_or_404(
        session, username, (joinedload(Usuario.accesos), joinedload(Usuario.roles))
    )
    return usuario


@router.get("/", response_model=UsuarioListSchema)
def list_usuarios(session: SessionDependency):
    usuarios = crud_usuario.get_multi(
        session,
        options=(joinedload(Usuario.accesos), joinedload(Usuario.roles)),
        apply_unique=True,
    )
    return UsuarioListSchema(data=usuarios)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_usuario(session: SessionDependency, usuario: UsuarioCreateSchema):
    usuario.password = get_password_hash(usuario.password)
    exists = crud_usuario.get_by_pk(session, usuario.username)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Usuario {usuario.username} ya existe",
        )

    message, db_usuario = crud_usuario.create(session, usuario, commit=False)

    if usuario.rol_ids:
        for rol_id in set(usuario.rol_ids):
            rol = crud_rol.get_by_pk_or_404(session, rol_id)
            db_usuario.roles.append(rol)

    if usuario.acceso_ids:
        for acceso_id in set(usuario.acceso_ids):
            acceso = crud_acceso.get_by_pk_or_404(session, acceso_id)
            db_usuario.accesos.append(acceso)

    session.add(db_usuario)
    session.commit()
    return {"message": message}


@router.put("/{username}")
def update_usuario(
    session: SessionDependency, username: str, usuario: UsuarioUpdateSchema
):
    db_usuario = crud_usuario.get_by_pk_or_404(session, username)
    message, _ = crud_usuario.update(
        session, db_usuario, usuario.model_dump(exclude_unset=True)
    )

    return {"message": message}


@router.delete("/{username}")
def delete_usuario(session: SessionDependency, username: str):
    usuario = crud_usuario.get_by_pk_or_404(session, username)
    message = crud_usuario.delete(session, usuario)
    return {"message": message}
