from core.database import SessionDependency
from fastapi import APIRouter, Body, HTTPException, status
from sqlalchemy.orm import joinedload

from security.cruds import (
    crud_rol,
    crud_usuario,
    crud_usuario_rol,
    validate_usuario_data,
)
from security.models import Usuario, UsuarioRol
from security.schemas import (
    UsuarioCreateSchema,
    UsuarioListSchema,
    UsuarioSchema,
    UsuarioUpdateSchema,
)
from security.utils import get_password_hash

router = APIRouter(tags=["Seguridad - Usuarios"], prefix="/usuarios")


@router.get("/{usuario_id}", response_model=UsuarioSchema)
def get_usuario(session: SessionDependency, usuario_id: int):
    usuario = crud_usuario.get_by_pk_or_404(
        session, usuario_id, [joinedload(Usuario.roles)]
    )
    return usuario


@router.get("/", response_model=UsuarioListSchema)
def list_usuarios(session: SessionDependency):
    usuarios = crud_usuario.get_multi(
        session,
        options=[joinedload(Usuario.roles)],
        apply_unique=True,
    )
    return UsuarioListSchema(usuarios=usuarios)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_usuario(session: SessionDependency, usuario: UsuarioCreateSchema):
    is_valid, detail = validate_usuario_data(session, usuario)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    usuario.password = get_password_hash(usuario.password)
    message, db_usuario = crud_usuario.create(session, usuario, commit=False)

    if usuario.rol_ids:
        for rol_id in set(usuario.rol_ids):
            rol = crud_rol.get_by_pk_or_404(session, rol_id)
            crud_usuario_rol.create(
                session,
                UsuarioRol(usuario_id=db_usuario.usuario_id, rol_id=rol.rol_id),
                commit=False,
            )

    session.commit()
    return {"message": message}


@router.put("/{usuario_id}")
def update_usuario(
    session: SessionDependency, usuario_id: int, usuario: UsuarioUpdateSchema
):
    db_usuario = crud_usuario.get_by_pk_or_404(session, usuario_id)

    is_valid, detail = validate_usuario_data(session, usuario)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    message, _ = crud_usuario.update(
        session, db_usuario, usuario.model_dump(exclude_unset=True)
    )

    return {"message": message}


@router.delete("/{usuario_id}")
def delete_usuario(session: SessionDependency, usuario_id: str):
    usuario = crud_usuario.get_by_pk_or_404(session, usuario_id)
    message = crud_usuario.delete(session, usuario)
    return {"message": message}


#######################################################


@router.post("/{usuario_id}/roles/")
def add_roles_to_usuario(
    session: SessionDependency, usuario_id: int, rol_ids: list[int] = Body(embed=True)
):
    usuario = crud_usuario.get_by_pk_or_404(session, usuario_id)
    for rol_id in set(rol_ids):
        rol = crud_rol.get_by_pk_or_404(session, rol_id)
        exists = crud_usuario_rol.get_by_pk(
            session, {"usuario_id": usuario_id, "rol_id": rol_id}
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Usuario {usuario.username} ya tiene el rol: {rol.nombre}",
            )
        crud_usuario_rol.create(
            session,
            UsuarioRol(usuario_id=usuario.usuario_id, rol_id=rol.rol_id),
            commit=False,
        )

    session.commit()
    return {"message": "Roles añadidos"}


@router.delete("/{usuario_id}/roles/")
def delete_roles_from_usuario(
    session: SessionDependency, usuario_id: int, rol_ids: list[int] = Body(embed=True)
):
    usuario = crud_usuario.get_by_pk_or_404(session, usuario_id)
    for rol_id in set(rol_ids):
        usuario_rol = crud_usuario_rol.get_by_pk(
            session, {"usuario_id": usuario_id, "rol_id": rol_id}
        )

        if not usuario_rol:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Usuario {usuario.username} no tiene el rol con ID: {rol_id}",
            )
        session.delete(usuario_rol)

    session.commit()
    return {"message": "Roles eliminados"}
