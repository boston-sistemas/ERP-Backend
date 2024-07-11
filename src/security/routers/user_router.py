from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.schemas import (
    UsuarioCreateWithRolesSchema,
    UsuarioListSchema,
    UsuarioSchema,
    UsuarioUpdateSchema,
)
from src.security.services import UserService

router = APIRouter(tags=["Seguridad - Usuarios"], prefix="/usuarios")

"""
# TODO: Analizar si inyectar como dependencia la busqueda de un usuario por id
"""


@router.get("/{usuario_id}", response_model=UsuarioSchema)
async def read_user(usuario_id: int, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)

    result = await user_service.read_user(usuario_id, include_roles=True)
    if result.is_success:
        return result.value

    raise result.error


@router.get("/", response_model=UsuarioListSchema)
async def read_users(db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)

    usuarios = await user_service.read_users()

    return UsuarioListSchema(usuarios=usuarios)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user_with_roles(
    user_data: UsuarioCreateWithRolesSchema, db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)

    creation_result = await user_service.create_user_with_roles(user_data)
    if creation_result.is_success:
        if user_data.rol_ids:
            return {"message": "Usuario creado y roles añadidos."}

        return {"message": "Usuario creado"}

    raise creation_result.error


@router.patch("/{usuario_id}")
async def update_usuario(
    usuario_id: int,
    update_data: UsuarioUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)

    result = await service.update_user(usuario_id, update_data)
    if result.is_success:
        return {"message": "Usuario actualizado"}

    raise result.error


@router.delete("/{usuario_id}")
async def delete_user(usuario_id: int, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)

    result = await user_service.delete_user(usuario_id)
    if result.is_success:
        return {"message": "Usuario eliminado correctamente"}

    raise result.error


#######################################################


@router.post("/{usuario_id}/roles/")
async def add_roles_to_user(
    usuario_id: int,
    rol_ids: list[int] = Body(embed=True),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    result = await user_service.add_roles_to_user(usuario_id, rol_ids)
    if result.is_success:
        return {"message": "Roles añadidos correctamente"}

    raise result.error


@router.delete("/{usuario_id}/roles/")
async def delete_roles_from_user(
    usuario_id: int,
    rol_ids: list[int] = Body(embed=True),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    result = await user_service.delete_roles_from_user(usuario_id, rol_ids)
    if result.is_success:
        return {"message": "Roles eliminados correctamente"}

    raise result.error
