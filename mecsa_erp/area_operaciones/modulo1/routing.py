from fastapi import APIRouter

from config.database import SessionDependency
from helpers.crud import CRUD
from mecsa_erp.area_operaciones.modulo0.models import (
    OrdenServicioTejeduria,
    OrdenServicioTejeduriaDetalle,
)
from mecsa_erp.area_operaciones.modulo1.schemas import (
    OrdenServicioTejeduriaDetalleListUpdateSchema,
    OrdenServicioTejeduriaUpdateSchema,
    RevisionStock,
    ReporteStock,
)

crud_orden_servicio_tejeduria = CRUD[OrdenServicioTejeduria, OrdenServicioTejeduria](
    OrdenServicioTejeduria
)
crud_orden_servicio_detalle_tejeduria = CRUD[
    OrdenServicioTejeduriaDetalle, OrdenServicioTejeduriaDetalle
](OrdenServicioTejeduriaDetalle)

router = APIRouter(prefix="/operations/v1", tags=["Area Operaciones"])


@router.get("/reporte-stock", response_model=ReporteStock)
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


@router.put("/reporte-stock/subordenes")
def reporte_stock_update_suborders(
    body: OrdenServicioTejeduriaDetalleListUpdateSchema, session: SessionDependency
):
    subordenes = body.subordenes
    for suborden in subordenes:
        db_suborden = crud_orden_servicio_detalle_tejeduria.get_by_pk_or_404(
            session,
            {
                "orden_servicio_tejeduria_id": suborden.orden_servicio_tejeduria_id,
                "crudo_id": suborden.crudo_id,
            },
        )
        crud_orden_servicio_detalle_tejeduria.update(
            session,
            db_suborden,
            suborden.model_dump(
                exclude={"orden_servicio_tejeduria_id", "crudo_id"}, exclude_unset=True
            ),
            commit=False,
        )
    session.commit()
    return {"message": "Subordenes actualizadas"}


@router.put("/reporte-stock/ordenes")
def reporte_stock_update_orders(
    orders: list[OrdenServicioTejeduriaUpdateSchema], session: SessionDependency
):
    pass


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
