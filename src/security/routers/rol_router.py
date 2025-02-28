from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.schemas import (
    RolCreateAccessWithOperationSchema,
    RolCreateWithAccesosSchema,
    RolDeleteAccessWithOperationSchema,
    RolListSchema,
    RolSchema,
    RolUpdateSchema,
)
from src.security.services import RolService

router = APIRouter(tags=["Seguridad - Roles"], prefix="/roles")


@router.get("/{rol_id}", response_model=RolSchema)
async def read_rol(rol_id: int, db: AsyncSession = Depends(get_db)):
    rol_service = RolService(db)

    result = await rol_service.read_rol(rol_id, include_access_operation=True)
    if result.is_success:
        return result.value

    raise result.error


@router.get("/", response_model=RolListSchema)
async def read_roles(db: AsyncSession = Depends(get_db)):
    service = RolService(db)
    result = await service.read_roles()

    if result.is_success:
        return result.value

    raise result.error


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rol_with_accesos(
    rol_data: RolCreateWithAccesosSchema, db: AsyncSession = Depends(get_db)
):
    rol_service = RolService(db)

    creation_result = await rol_service.create_rol_with_accesos(rol_data)
    if creation_result.is_success:
        return creation_result.value

    raise creation_result.error


@router.patch("/{rol_id}")
async def update_rol(
    rol_id: int, update_data: RolUpdateSchema, db: AsyncSession = Depends(get_db)
):
    rol_service = RolService(db)

    result = await rol_service.update_rol(rol_id, update_data)
    if result.is_success:
        return {"message": "Rol actualizado"}

    raise result.error


@router.delete("/{rol_id}")
async def delete_rol(rol_id: int, db: AsyncSession = Depends(get_db)):
    rol_service = RolService(db)

    result = await rol_service.delete_rol(rol_id)
    if result.is_success:
        return {"message": "Rol desactivado correctamente"}

    raise result.error


#######################################################


@router.post("/{rol_id}/accesos/")
async def add_accesos_to_rol(
    rol_id: int,
    form: RolCreateAccessWithOperationSchema,
    db: AsyncSession = Depends(get_db),
):
    rol_service = RolService(db)

    result = await rol_service.add_accesos_to_rol(rol_id=rol_id, form=form)
    if result.is_success:
        return result.value

    raise result.error


@router.delete("/{rol_id}/accesos/")
async def delete_accesos_from_rol(
    rol_id: int,
    form: RolDeleteAccessWithOperationSchema,
    db: AsyncSession = Depends(get_db),
):
    rol_service = RolService(db)

    result = await rol_service.delete_accesos_from_rol(rol_id=rol_id, form=form)
    if result.is_success:
        return result.value

    raise result.error
