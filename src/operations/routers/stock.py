from fastapi import APIRouter

from src.core.database import SessionDependency
from src.operations.cruds import (
    crud_orden_servicio_tejeduria,
    crud_orden_servicio_tejeduria_detalle,
)
from src.operations.models import OrdenServicioTejeduria
from src.operations.schemas import (
    OrdenServicioTejeduriaDetalleListUpdateSchema,
    OrdenServicioTejeduriaListUpdateSchema,
    ReporteStock,
    RevisionStock,
)

router = APIRouter()


@router.get("/reporte-stock", response_model=ReporteStock)
def reporte_stock(session: SessionDependency):
    # TODO: Encontrar el codigo del proveedor asociado al usuario
    proveedor_id = "P006"
    ordenes = crud_orden_servicio_tejeduria.get_multi(
        session,
        (
            (OrdenServicioTejeduria.tejeduria_id == proveedor_id)
            &
            (OrdenServicioTejeduria.estado == "PENDIENTE")
        ),
    )

    return ReporteStock(ordenes=ordenes)


@router.put("/reporte-stock/subordenes")
def reporte_stock_update_suborders(
    body: OrdenServicioTejeduriaDetalleListUpdateSchema, session: SessionDependency
):
    subordenes = body.subordenes
    for suborden in subordenes:
        db_suborden = crud_orden_servicio_tejeduria_detalle.get_by_pk_or_404(
            session,
            {
                "orden_servicio_tejeduria_id": suborden.orden_servicio_tejeduria_id,
                "crudo_id": suborden.crudo_id,
            },
        )
        crud_orden_servicio_tejeduria_detalle.update(
            session,
            db_suborden,
            suborden.model_dump(
                exclude={"orden_servicio_tejeduria_id", "crudo_id"}, exclude_none=True
            ),
            commit=False,
        )
    session.commit()
    return {"message": "Subordenes actualizadas"}


@router.get("/revision-stock", response_model=RevisionStock)
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


@router.put("/revision-stock/ordenes")
def revision_stock_update_orders(
    body: OrdenServicioTejeduriaListUpdateSchema, session: SessionDependency
):
    ordenes = body.ordenes
    for orden in ordenes:
        db_orden = crud_orden_servicio_tejeduria.get_by_pk_or_404(
            session, orden.orden_servicio_tejeduria_id
        )
        crud_orden_servicio_tejeduria.update(
            session,
            db_orden,
            orden.model_dump(exclude={"orden_servicio_tejeduria_id"}),
            commit=False,
        )
    session.commit()
    return {"message": "Ordenes actualizadas"}
