from fastapi import APIRouter, Body, HTTPException, status

from src.core.database import SessionDependency
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
def get_rol(session: SessionDependency, rol_id: int):
    session = RolService(session)
    rol = session.read_model_by_parameter(Rol, Rol.rol_id == rol_id)

    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rol {rol_id} no encontrado"
        )

    return rol


@router.get("/", response_model=RolListSchema)
def list_roles(session: SessionDependency):
    session = RolService(session)
    roles = session.read_rols()
    return RolListSchema(roles=roles)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_rol(session: SessionDependency, rol: RolCreateSchema):
    session = RolService(session)
    exists = session.read_model_by_parameter(Rol, Rol.nombre == rol.nombre)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rol {rol.nombre} ya existe",
        )

    rol = session.create_rol(rol)
    return rol


@router.put("/{rol_id}")
def update_rol(session: SessionDependency, rol_id: int, rol: RolUpdateSchema):
    session = RolService(session)
    exists = session.read_model_by_parameter(Rol, Rol.nombre == rol.nombre)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rol {rol.nombre} ya existe",
        )

    rol_update = session.read_model_by_parameter(Rol, Rol.rol_id == rol_id)
    if not rol_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rol {rol_id} no encontrado"
        )

    rol_update = session.update_rol(rol_update, rol)

    return rol_update


@router.delete("/{rol_id}")
def delete_rol(session: SessionDependency, rol_id: int):
    session = RolService(session)
    rol = session.read_model_by_parameter(Rol, Rol.rol_id == rol_id)
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rol {rol_id} no encontrado"
        )

    message = session.delete_rol(rol)
    return {"message": message}


#######################################################


@router.post("/{rol_id}/accesos/", response_model=RolSchema)
def add_accesos_to_rol(
    session: SessionDependency, rol_id: int, acceso_ids: list[int] = Body(embed=True)
):
    session = RolService(session)

    rol = session.read_model_by_parameter(Rol, Rol.rol_id == rol_id)
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rol {rol_id} no encontrado"
        )

    session.create_access_to_rol(rol_id, acceso_ids)

    return rol


@router.delete("/{rol_id}/accesos/", response_model=RolSchema)
def delete_accesos_from_rol(
    session: SessionDependency, rol_id: int, acceso_ids: list[int] = Body(embed=True)
):
    session = RolService(session)

    rol = session.read_model_by_parameter(Rol, Rol.rol_id == rol_id)

    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rol {rol_id} no encontrado"
        )

    result = session.delete_access_to_rol(rol_id, acceso_ids)

    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rol {rol.nombre} no tiene los accesos con ID: {result}",
        )

    return rol
