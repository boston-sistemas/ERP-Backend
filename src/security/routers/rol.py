from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.schemas import (
    RolCreateSchema,
    RolListSchema,
    RolSchema,
    RolUpdateSchema,
)
from src.security.services import RolService

router = APIRouter(tags=["Seguridad - Roles"], prefix="/roles")


@router.get("/{rol_id}", response_model=RolSchema)
async def read_rol(rol_id: int, db: AsyncSession = Depends(get_db)):
    rol_service = RolService(db)

    result = await rol_service.read_rol(rol_id, include_accesos=True)
    if result.is_success:
        return result.value

    raise result.error


@router.get("/", response_model=RolListSchema)
async def read_roles(db: AsyncSession = Depends(get_db)):
    rol_service = RolService(db)

    roles = await rol_service.read_roles()

    return RolListSchema(roles=roles)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rol(rol_data: RolCreateSchema, db: AsyncSession = Depends(get_db)):
    rol_service = RolService(db)

    creation_result = await rol_service.create_rol(rol_data)
    if creation_result.is_success:
        return {"message": "Rol creado"}

    raise creation_result.error


@router.put("/{rol_id}")
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
        return {"message": "Rol eliminado correctamente"}

    raise result.error


#######################################################


@router.post("/{rol_id}/accesos/")
async def add_accesos_to_rol(
    rol_id: int,
    acceso_ids: list[int] = Body(embed=True),
    db: AsyncSession = Depends(get_db),
):
    rol_service = RolService(db)

    result = await rol_service.add_accesos_to_rol(rol_id, acceso_ids)
    if result.is_success:
        return {"message": "Accesos añadidos correctamente"}

    raise result.error


@router.delete("/{rol_id}/accesos/")
async def delete_accesos_from_rol(
    rol_id: int,
    acceso_ids: list[int] = Body(embed=True),
    db: AsyncSession = Depends(get_db),
):
    rol_service = RolService(db)

    result = await rol_service.delete_accesos_from_rol(rol_id, acceso_ids)
    if result.is_success:
        return {"message": "Accesos eliminados correctamente"}

    raise result.error
