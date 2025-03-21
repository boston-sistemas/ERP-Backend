from fastapi import APIRouter, Body, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.dependencies import get_current_user_id
from src.core.services import PermissionService
from src.security.audit import AuditService
from src.security.schemas import (
    UsuarioCreateWithRolesSchema,
    UsuarioListSchema,
    UsuarioSchema,
    UsuarioUpdatePasswordSchema,
    UsuarioUpdateSchema,
)
from src.security.services import UserService

router = APIRouter(tags=["Seguridad - Usuarios"], prefix="/usuarios")

"""
# TODO: Analizar si inyectar como dependencia la busqueda de un usuario por id
"""


@router.get(
    "/{usuario_id}", response_model=UsuarioSchema, status_code=status.HTTP_200_OK
)
# @PermissionService.check_permission(1, 101)
@AuditService.audit_action_log()
async def read_user(
    request: Request,
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    result = await user_service.read_user(usuario_id, include_roles=True)
    if result.is_success:
        return result.value

    raise result.error


@router.get("/", response_model=UsuarioListSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def read_users(request: Request, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)

    usuarios = await user_service.read_users()

    return UsuarioListSchema(usuarios=usuarios)


@router.post("/", status_code=status.HTTP_201_CREATED)
@AuditService.audit_action_log()
async def create_user_with_roles(
    request: Request,
    user_data: UsuarioCreateWithRolesSchema,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    creation_result = await user_service.create_user_with_roles(user_data)
    if creation_result.is_success:
        if user_data.rol_ids:
            return {"message": "Usuario creado y roles añadidos."}

        return {"message": "Usuario creado"}

    raise creation_result.error


@router.patch("/{usuario_id}", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def update_usuario(
    request: Request,
    usuario_id: int,
    update_data: UsuarioUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)

    result = await service.update_user(usuario_id, update_data)
    if result.is_success:
        return {"message": "Usuario actualizado"}

    raise result.error


@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def delete_user(
    request: Request, usuario_id: int, db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)

    result = await user_service.delete_user(usuario_id)
    if result.is_success:
        return {"message": "Usuario eliminado correctamente"}

    raise result.error


#######################################################


@router.post("/{usuario_id}/roles/", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def add_roles_to_user(
    request: Request,
    usuario_id: int,
    rol_ids: list[int] = Body(embed=True),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    result = await user_service.add_roles_to_user(usuario_id, rol_ids)
    if result.is_success:
        return {"message": "Roles añadidos correctamente"}

    raise result.error


@router.delete("/{usuario_id}/roles/", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def delete_roles_from_user(
    request: Request,
    usuario_id: int,
    rol_ids: list[int] = Body(embed=True),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    result = await user_service.delete_roles_from_user(usuario_id, rol_ids)
    if result.is_success:
        return {"message": "Roles eliminados correctamente"}

    raise result.error


@router.put("/me/password", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def update_password(
    request: Request,
    update_password: UsuarioUpdatePasswordSchema,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    result = await user_service.update_password(
        current_user_id, update_password.new_password
    )

    if result.is_success:
        return {"message": "Contraseña actualizada correctamente"}

    raise result.error


@router.put("/{usuario_id}/reset-password", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def reset_password(
    request: Request,
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    result = await user_service.reset_password(usuario_id)

    if result.is_success:
        return {"message": "Contraseña reiniciada correctamente"}

    raise result.error
