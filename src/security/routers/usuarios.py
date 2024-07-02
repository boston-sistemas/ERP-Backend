from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
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
async def get_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    session = UserService(db)
    user = await session.read_model_by_parameter(
        Usuario, Usuario.usuario_id == usuario_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado",
        )

    return user


@router.get("/", response_model=UsuarioListSchema)
async def list_usuarios(db: AsyncSession = Depends(get_db)):
    session = UserService(db)

    usuarios = await session.read_users()

    return UsuarioListSchema(usuarios=usuarios)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UsuarioSchema)
async def create_usuario(
    usuario: UsuarioCreateSchema, db: AsyncSession = Depends(get_db)
):
    session = UserService(db)

    exists = await session.read_model_by_parameter(
        Usuario, Usuario.username == usuario.username
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Usuario {usuario.username} ya existe",
        )

    usuario.password = get_password_hash(usuario.password)

    user = await session.create_user(usuario)

    return user


@router.patch("/{usuario_id}", response_model=UsuarioSchema)
async def update_usuario(
    usuario_id: int, usuario: UsuarioUpdateSchema, db: AsyncSession = Depends(get_db)
):
    session = UserService(db)
    exists = await session.read_model_by_parameter(
        Usuario, Usuario.username == usuario.username
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Usuario {usuario.username} ya existe",
        )

    user_update = await session.read_model_by_parameter(
        Usuario, Usuario.usuario_id == usuario_id
    )

    if not user_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado",
        )

    user_update = await session.update_user(user_update, usuario)

    return user_update


@router.delete("/{usuario_id}")
async def delete_usuario(usuario_id: str = None, db: AsyncSession = Depends(get_db)):
    session = UserService(db)
    usuario = await session.read_model_by_parameter(
        Usuario, Usuario.usuario_id == usuario_id
    )
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado",
        )

    message = await session.delete_user(usuario)

    return {"message": message}


#######################################################


@router.post("/{usuario_id}/roles/", response_model=UsuarioSchema)
async def add_roles_to_usuario(
    usuario_id: int,
    rol_ids: list[int] = Body(embed=True),
    db: AsyncSession = Depends(get_db),
):
    session = UserService(db)
    usuario = await session.read_model_by_parameter(
        Usuario, Usuario.usuario_id == usuario_id
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado",
        )

    await session.create_rol_to_user(usuario_id, rol_ids)

    usuario = await session.refresh_user(usuario)
    # print(usuario)

    return usuario


@router.delete("/{usuario_id}/roles/", response_model=UsuarioSchema)
async def delete_roles_from_usuario(
    usuario_id: int,
    rol_ids: list[int] = Body(embed=True),
    db: AsyncSession = Depends(get_db),
):
    session = UserService(db)
    usuario = await session.read_model_by_parameter(
        Usuario, Usuario.usuario_id == usuario_id
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado",
        )

    result = await session.delete_rol_to_user(usuario_id, rol_ids)

    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Usuario {usuario.username} no tiene el rol con ID: {result}",
        )

    usuario = await session.refresh_user(usuario)

    return usuario
