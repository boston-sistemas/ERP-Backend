from fastapi import APIRouter
from sqlmodel import Session, select
from config.database import SessionDependency

from ..models import OrdenServicioTejeduria
from ..schemas.orden_servicio_tejeduria import OrdenServicioTejeduriaListSchema

router = APIRouter(
    tags=["Modulo 0 - O/S Tejeduria"], prefix="/orden-servicio-tejeduria"
)

def get_orden_servicio_tejeduria_by_estado(session: Session, estado: str):
    statement = select(OrdenServicioTejeduria).where(
        OrdenServicioTejeduria.estado == estado
    )
    items = session.exec(statement).all()
    return items


@router.get(
    path="/",
    name=f"Listar O/S Tejeduria",
    response_model=OrdenServicioTejeduriaListSchema,
)
def get_orden_servicio_tejeduria(session: SessionDependency):
    statement = select(OrdenServicioTejeduria)
    items = session.exec(statement).all()
    return OrdenServicioTejeduriaListSchema(data=items, count=len(items))


@router.get(
    path="/estado/pendiente",
    name=f"Listar O/S Tejeduria pendientes",
    response_model=OrdenServicioTejeduriaListSchema,
)
def get_orden_servicio_tejeduria_estado_pendiente(
    session: SessionDependency,
):
    items = get_orden_servicio_tejeduria_by_estado(session, "PENDIENTE")
    return OrdenServicioTejeduriaListSchema(data=items, count=len(items))


@router.get(
    path="/estado/cerrado",
    name=f"Listar O/S Tejeduria cerradas",
    response_model=OrdenServicioTejeduriaListSchema,
)
def get_orden_servicio_tejeduria_estado_cerrado(
    session: SessionDependency,
):
    items = get_orden_servicio_tejeduria_by_estado(session, "CERRADO")
    return OrdenServicioTejeduriaListSchema(data=items, count=len(items))