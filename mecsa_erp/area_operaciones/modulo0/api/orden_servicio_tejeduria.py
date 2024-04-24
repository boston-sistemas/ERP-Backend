from typing import Optional
from fastapi import APIRouter
from sqlmodel import Session, select
from config.database import SessionDependency

from ..models import OrdenServicioTejeduria
from ..schemas.orden_servicio_tejeduria import OrdenServicioTejeduriaListSchema

router = APIRouter(
    tags=["Modulo 0 - O/S Tejeduria"], prefix="/orden-servicio-tejeduria"
)

def get_orden_servicio_tejeduria_filtering(session: Session, tejeduria_id: str = None, estado: str = None):
    query = select(OrdenServicioTejeduria)
    
    if tejeduria_id:
        query = query.where(OrdenServicioTejeduria.tejeduria_id == tejeduria_id)

    if estado:
        query = query.where(OrdenServicioTejeduria.estado == estado)

    return session.exec(query).all()

@router.get(
    path="/",
    name=f"Listar O/S Tejeduria",
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
    items = get_orden_servicio_tejeduria_filtering(session, tejeduria_id=tejeduria_id, estado="PENDIENTE")
    return OrdenServicioTejeduriaListSchema(data=items, count=len(items))