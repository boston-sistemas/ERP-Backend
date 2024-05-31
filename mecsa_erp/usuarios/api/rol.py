from fastapi import APIRouter, Body, HTTPException, status
from sqlalchemy.orm import joinedload

from config.database import SessionDependency
from helpers.crud import CRUD

from mecsa_erp.usuarios.models import Acceso, Rol, RolAcceso
from mecsa_erp.usuarios.schemas.usuario import (
    RolCreateSchema,
    RolListSchema,
    RolSchema,
    RolUpdateSchema,
)

crud_acceso = CRUD[Acceso, Acceso](Acceso)
crud_rol = CRUD[Rol, RolCreateSchema](Rol)
crud_rol_acceso = CRUD[RolAcceso, RolAcceso](RolAcceso)

router = APIRouter(tags=["Roles"], prefix="/roles")


@router.get("/{rol_id}", response_model=RolSchema)
def get_rol(session: SessionDependency, rol_id: int):
    rol = crud_rol.get_by_pk_or_404(session, rol_id, [joinedload(Rol.accesos)])
    return rol


@router.get("/", response_model=RolListSchema)
def list_roles(session: SessionDependency):
    roles = crud_rol.get_multi(
        session, options=[joinedload(Rol.accesos)], apply_unique=True
    )
    return RolListSchema(data=roles)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_rol(session: SessionDependency, rol: RolCreateSchema):
    exists = crud_rol.get(session, Rol.nombre == rol.nombre)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rol {rol.nombre} ya existe",
        )

    message, db_rol = crud_rol.create(session, rol, commit=False)

    if rol.acceso_ids:
        for acceso_id in set(rol.acceso_ids):
            acceso = crud_acceso.get_by_pk_or_404(session, acceso_id)
            crud_rol_acceso.create(
                session,
                RolAcceso(rol_id=db_rol.rol_id, acceso_id=acceso.acceso_id),
                commit=False,
            )

    session.commit()
    return {"message": message}


@router.put("/{rol_id}")
def update_rol(session: SessionDependency, rol_id: int, rol: RolUpdateSchema):
    db_rol = crud_rol.get_by_pk_or_404(session, rol_id)

    exists = rol.nombre and crud_rol.get(session, Rol.nombre == rol.nombre)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rol {rol.nombre} ya existe",
        )

    message, _ = crud_rol.update(session, db_rol, rol.model_dump(exclude_unset=True))

    return {"message": message}


@router.delete("/{rol_id}")
def delete_rol(session: SessionDependency, rol_id: int):
    rol = crud_rol.get_by_pk_or_404(session, rol_id)
    message = crud_rol.delete(session, rol)
    return {"message": message}


#######################################################


@router.post("/{rol_id}/accesos/")
def add_accesos_to_rol(
    session: SessionDependency, rol_id: int, acceso_ids: list[int] = Body(embed=True)
):
    rol = crud_rol.get_by_pk_or_404(session, rol_id)
    for acceso_id in set(acceso_ids):
        acceso = crud_acceso.get_by_pk_or_404(session, acceso_id)
        exists = crud_rol_acceso.get_by_pk(
            session, {"rol_id": rol.rol_id, "acceso_id": acceso.acceso_id}
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Rol {rol.nombre} ya tiene el acceso: {acceso.nombre}",
            )
        crud_rol_acceso.create(
            session,
            RolAcceso(rol_id=rol.rol_id, acceso_id=acceso.acceso_id),
            commit=False,
        )

    session.commit()
    return {"message": "Accesos añadidos"}


@router.delete("/{rol_id}/accesos/")
def delete_accesos_from_rol(
    session: SessionDependency, rol_id: int, acceso_ids: list[int] = Body(embed=True)
):
    rol = crud_rol.get_by_pk_or_404(session, rol_id)
    for acceso_id in set(acceso_ids):
        rol_acceso = crud_rol_acceso.get_by_pk(
            session, {"rol_id": rol_id, "acceso_id": acceso_id}
        )

        if not rol_acceso:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Rol {rol.nombre} no tiene el acceso con ID: {acceso_id}",
            )
        session.delete(rol_acceso)

    session.commit()
    return {"message": "Accesos eliminados"}
