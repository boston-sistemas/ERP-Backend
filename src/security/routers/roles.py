from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.models import Rol
from src.security.schemas import (
    RolCreateSchema,
    RolListSchema,
    RolSchema,
    RolUpdateSchema,
)
from src.security.services.rol_services import RolService

router = APIRouter(tags=["Seguridad - Roles"], prefix="/roles")


@router.get("/{rol_id}", response_model=RolSchema)
async def get_rol(rol_id: int, db: AsyncSession = Depends(get_db)):
    service = RolService(db)
    rol = await service.read_model_by_parameter(Rol, Rol.rol_id == rol_id)

    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rol {rol_id} no encontrado"
        )

    return rol


@router.get("/", response_model=RolListSchema)
async def list_roles(db: AsyncSession = Depends(get_db)):
    session = RolService(db)
    roles = await session.read_rols()
    return RolListSchema(roles=roles)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rol(rol: RolCreateSchema, db: AsyncSession = Depends(get_db)):
    session = RolService(db)
    exists = await session.read_model_by_parameter(Rol, Rol.nombre == rol.nombre)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rol {rol.nombre} ya existe",
        )

    rol = await session.create_rol(rol)
    return rol


@router.put("/{rol_id}")
async def update_rol(
    rol_id: int, rol: RolUpdateSchema, db: AsyncSession = Depends(get_db)
):
    session = RolService(db)
    exists = await session.read_model_by_parameter(Rol, Rol.nombre == rol.nombre)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rol {rol.nombre} ya existe",
        )

    rol_update = await session.read_model_by_parameter(Rol, Rol.rol_id == rol_id)
    if not rol_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rol {rol_id} no encontrado"
        )

    rol_update = await session.update_rol(rol_update, rol)

    return rol_update


@router.delete("/{rol_id}")
async def delete_rol(rol_id: int, db: AsyncSession = Depends(get_db)):
    session = RolService(db)
    rol = await session.read_model_by_parameter(Rol, Rol.rol_id == rol_id)
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rol {rol_id} no encontrado"
        )

    message = await session.delete_rol(rol)
    return {"message": message}


#######################################################


@router.post("/{rol_id}/accesos/", response_model=RolSchema)
async def add_accesos_to_rol(
    rol_id: int,
    acceso_ids: list[int] = Body(embed=True),
    db: AsyncSession = Depends(get_db),
):
    session = RolService(db)

    rol = await session.read_model_by_parameter(Rol, Rol.rol_id == rol_id)
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rol {rol_id} no encontrado"
        )

    await session.create_access_to_rol(rol_id, acceso_ids)
    rol = await session.refresh_rol(rol)

    return rol


@router.delete("/{rol_id}/accesos/", response_model=RolSchema)
async def delete_accesos_from_rol(
    rol_id: int,
    acceso_ids: list[int] = Body(embed=True),
    db: AsyncSession = Depends(get_db),
):
    session = RolService(db)

    rol = await session.read_model_by_parameter(Rol, Rol.rol_id == rol_id)

    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rol {rol_id} no encontrado"
        )

    result = await session.delete_access_to_rol(rol_id, acceso_ids)

    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rol {rol.nombre} no tiene los accesos con ID: {result}",
        )

    rol = await session.refresh_rol(rol)

    return rol
