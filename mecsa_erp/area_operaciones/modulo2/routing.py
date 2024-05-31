from fastapi import APIRouter

from config.database import SessionDependency

from mecsa_erp.area_operaciones.modulo0.models import OrdenServicioTejeduria
from mecsa_erp.area_operaciones.modulo2.schemas import ProgramacionTintoreria
from mecsa_erp.area_operaciones.modulo1.routing import crud_orden_servicio_tejeduria

router = APIRouter(tags=["Módulo 2"], prefix="/modulo2")


@router.get("/programacion-tintoreria")
def programacion_tintoreria(session: SessionDependency):
    pendientes = crud_orden_servicio_tejeduria.get_multi(
        session,
        OrdenServicioTejeduria.estado == "PENDIENTE",
    )

    items = [
        detalle
        for orden in pendientes
        for detalle in orden.detalles
        if detalle.reporte_tejeduria_nro_rollos > 0
    ]

    return ProgramacionTintoreria(subordenes=items)
