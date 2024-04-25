from typing import Optional
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from config.database import SessionDependency

from ..models import OrdenServicioTejeduria
from ..schemas.orden_servicio_tejeduria import (
    OrdenServicioTejeduriaListSchema,
    OrdenServicioTejeduriaSimpleListSchema,
    OrdenServicioTejeduriaSimpleSchema,
    OrdenServicioTejeduriaUpdateMultipleSchema,
    OrdenServicioTejeduriaUpdateSchema,
)

router = APIRouter(
    tags=["Modulo 0 - O/S Tejeduria"], prefix="/orden-servicio-tejeduria"
)


def get_orden_servicio_tejeduria_filtering(
    session: Session, tejeduria_id: str = None, estado: str = None
):
    query = select(OrdenServicioTejeduria)

    if tejeduria_id:
        query = query.where(OrdenServicioTejeduria.tejeduria_id == tejeduria_id)

    if estado:
        query = query.where(OrdenServicioTejeduria.estado == estado)

    return session.exec(query).all()


@router.get(
    path="/",
    name="Listar O/S Tejeduria",
    response_model=OrdenServicioTejeduriaListSchema,
)
def get_orden_servicio_tejeduria(session: SessionDependency):
    items = get_orden_servicio_tejeduria_filtering(session)
    return OrdenServicioTejeduriaListSchema(data=items, count=len(items))


@router.get(
    path="/estado/pendiente",
    name="Listar O/S Tejeduria pendientes",
    response_model=OrdenServicioTejeduriaListSchema,
)
def get_orden_servicio_tejeduria_estado_pendiente(
    session: SessionDependency,
):
    items = get_orden_servicio_tejeduria_filtering(session, estado="PENDIENTE")
    return OrdenServicioTejeduriaListSchema(data=items, count=len(items))


@router.get(
    path="/estado/cerrado",
    name="Listar O/S Tejeduria cerradas",
    response_model=OrdenServicioTejeduriaListSchema,
)
def get_orden_servicio_tejeduria_estado_cerrado(
    session: SessionDependency,
):
    items = get_orden_servicio_tejeduria_filtering(session, estado="CERRADO")
    return OrdenServicioTejeduriaListSchema(data=items, count=len(items))


@router.get(
    path="/{tejeduria_id}/estado/pendiente",
    name="Listar O/S Tejeduria pendientes por Tejeduria",
    response_model=OrdenServicioTejeduriaListSchema,
)
def get_orden_servicio_tejeduria_estado_pendiente(
    session: SessionDependency,
    tejeduria_id: str,
):
    items = get_orden_servicio_tejeduria_filtering(
        session, tejeduria_id=tejeduria_id, estado="PENDIENTE"
    )
    return OrdenServicioTejeduriaListSchema(data=items, count=len(items))


@router.patch(
    path="/{orden_servicio_tejeduria_id}",
    name="Actualizar O/S Tejeduria",
    response_model=OrdenServicioTejeduriaSimpleSchema,
)
def update_orden_servicio_tejeduria(
    session: SessionDependency,
    orden_servicio_tejeduria_id: str,
    data: OrdenServicioTejeduriaUpdateSchema,
):
    orden_servicio_tejeduria = session.get(
        OrdenServicioTejeduria, orden_servicio_tejeduria_id
    )

    if not orden_servicio_tejeduria:
        raise HTTPException(
            status_code=404,
            detail=f"O/S Tejeduria {orden_servicio_tejeduria_id} no encontrado",
        )

    update_dict = data.model_dump(exclude_unset=True)
    orden_servicio_tejeduria.sqlmodel_update(update_dict)
    session.add(orden_servicio_tejeduria)
    session.commit()
    session.refresh(orden_servicio_tejeduria)
    return orden_servicio_tejeduria


@router.patch(
    path="/",
    name="Actualizar multiples O/S Tejeduria",
    response_model=OrdenServicioTejeduriaSimpleListSchema,
)
def update_multiple_orden_servicio_tejeduria(
    session: SessionDependency,
    data_list: OrdenServicioTejeduriaUpdateMultipleSchema,
):
    # TODO: Refactorizar las variables
    # TODO: Manejar la excepción si el ID no existe
    data_updated = []
    for orden_servicio_tejeduria in data_list.data:
        data = update_orden_servicio_tejeduria(
            session,
            orden_servicio_tejeduria.orden_servicio_tejeduria_id,
            orden_servicio_tejeduria,
        )
        data_updated.append(data)

    return OrdenServicioTejeduriaSimpleListSchema(
        data=data_updated, count=len(data_updated)
    )
