from fastapi import APIRouter

from config.database import SessionDependency
from helpers.crud import CRUD
from mecsa_erp.area_operaciones.modulo0.models import OrdenServicioTejeduria
from mecsa_erp.area_operaciones.modulo1.schemas import RevisionStock, ReporteStock

crud_orden_servicio_tejeduria = CRUD[OrdenServicioTejeduria, OrdenServicioTejeduria](
    OrdenServicioTejeduria
)

router = APIRouter(prefix="/operations/v1", tags=["Area Operaciones"])


@router.get("/reporte-stock")
def reporte_stock(session: SessionDependency):
    # TODO: Encontrar el codigo del proveedor asociado al usuario
    proveedor_id = "RSA"
    ordenes = crud_orden_servicio_tejeduria.get_multi(
        session,
        (
            (OrdenServicioTejeduria.tejeduria_id == proveedor_id)
            & (OrdenServicioTejeduria.estado == "PENDIENTE")
        ),
    )

    items = [detalle for orden in ordenes for detalle in orden.detalles]
    return ReporteStock(subordenes=items)


@router.get("/revision-stock")
def revision_stock(session: SessionDependency):
    pendientes = crud_orden_servicio_tejeduria.get_multi(
        session,
        (OrdenServicioTejeduria.estado == "PENDIENTE"),
    )

    cerrados = crud_orden_servicio_tejeduria.get_multi(
        session,
        (OrdenServicioTejeduria.estado == "CERRADO"),
    )

    return RevisionStock(ordenes_pendientes=pendientes, ordenes_cerradas=cerrados)
