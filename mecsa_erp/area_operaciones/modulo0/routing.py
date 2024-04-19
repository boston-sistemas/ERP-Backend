from fastapi import APIRouter, Depends
from sqlmodel import SQLModel, Session, select

from config.database import get_session
from mecsa_erp.area_operaciones.modulo0.models import OrdenServicioTejeduriaDetalle

router = APIRouter(tags=["Módulo 0"], prefix="/modulo0")

class OrdenServicioTejeduriaDetalleList(SQLModel):
    data: list[OrdenServicioTejeduriaDetalle]

@router.get("/orden-servicio-tejeduria-detalle", response_model=OrdenServicioTejeduriaDetalleList)
def get_orden_servicio_tejeduria_detalle(session: Session = Depends(get_session)):
    statement = select(OrdenServicioTejeduriaDetalle)
    objects = session.exec(statement).all()
    return OrdenServicioTejeduriaDetalleList(data=objects)