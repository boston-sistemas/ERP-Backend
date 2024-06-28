from fastapi import APIRouter, Body, HTTPException, status

from src.core.database import SessionDependency
from src.security.models import Usuario
from src.security.schemas import (
    UsuarioCreateSchema,
    UsuarioListSchema,
    UsuarioSchema,
    UsuarioUpdateSchema,
)
from src.security.services.users_services import UserService
from src.security.utils import get_password_hash

router = APIRouter(tags=["Seguridad - Usuarios"], prefix="/usuarios")


@router.get("/{usuario_id}", response_model=UsuarioSchema)
def get_usuario(session: SessionDependency, usuario_id: int):
    session = UserService(session)
    user = session.read_model_by_parameter(Usuario, Usuario.usuario_id == usuario_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado",
        )

    return user


@router.get("/", response_model=UsuarioListSchema)
def list_usuarios(session: SessionDependency):
    session = UserService(session)

    usuarios = session.read_users()

    return UsuarioListSchema(usuarios=usuarios)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UsuarioSchema)
def create_usuario(session: SessionDependency, usuario: UsuarioCreateSchema):
    session = UserService(session)

    exists = session.read_model_by_parameter(
        Usuario, Usuario.username == usuario.username
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Usuario {usuario.username} ya existe",
        )

    usuario.password = get_password_hash(usuario.password)

    usuario = session.create_user(usuario)

    return usuario


@router.patch("/{usuario_id}", response_model=UsuarioSchema)
def update_usuario(
    session: SessionDependency, usuario_id: int, usuario: UsuarioUpdateSchema
):
    session = UserService(session)
    exists = session.read_model_by_parameter(
        Usuario, Usuario.username == usuario.username
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Usuario {usuario.username} ya existe",
        )

    user_update = session.read_model_by_parameter(
        Usuario, Usuario.usuario_id == usuario_id
    )

    if not user_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado",
        )

    user_update = session.update_user(user_update, usuario)

    return user_update


@router.delete("/{usuario_id}")
def delete_usuario(session: SessionDependency, usuario_id: str):
    session = UserService(session)
    usuario = session.read_model_by_parameter(Usuario, Usuario.usuario_id == usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado",
        )

    message = session.delete_user(usuario)

    return {"message": message}


#######################################################


@router.post("/{usuario_id}/roles/", response_model=UsuarioSchema)
def add_roles_to_usuario(
    session: SessionDependency, usuario_id: int, rol_ids: list[int] = Body(embed=True)
):
    session = UserService(session)
    usuario = session.read_model_by_parameter(Usuario, Usuario.usuario_id == usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado",
        )

    session.create_rol_to_user(usuario_id, rol_ids)

    print(usuario)

    return usuario


@router.delete("/{usuario_id}/roles/", response_model=UsuarioSchema)
def delete_roles_from_usuario(
    session: SessionDependency, usuario_id: int, rol_ids: list[int] = Body(embed=True)
):
    session = UserService(session)
    usuario = session.read_model_by_parameter(Usuario, Usuario.usuario_id == usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado",
        )

    result = session.delete_rol_to_user(usuario_id, rol_ids)

    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Usuario {usuario.username} no tiene el rol con ID: {result}",
        )

    return usuario
