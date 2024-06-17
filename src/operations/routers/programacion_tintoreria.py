from core.database import SessionDependency
from fastapi import APIRouter
from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from operations.cruds import (
    crud_color,
    crud_orden_servicio_tejeduria,
    crud_orden_servicio_tejeduria_detalle,
    crud_proveedor,
    crud_servicio,
)
from operations.models import (
    OrdenServicioTejeduria,
    Partida,
    PartidaDetalle,
    ProgramacionTintoreria,
    Servicio,
)
from operations.schemas import (
    OrdenServicioTejeduriaWithDetallesListSchema,
    ProgramacionTintoreriaCreateSchema,
    ProgramacionTintoreriaResponse,
)

router = APIRouter()


@router.get("/programacion-tintoreria", response_model=ProgramacionTintoreriaResponse)
def programacion_tintoreria(session: SessionDependency):
    tejedurias = crud_servicio.get(
        session,
        filter=Servicio.nombre == "TEJEDURIA",
        options=[joinedload(Servicio.proveedores)],
    ).proveedores

    tintorerias = crud_servicio.get(
        session,
        filter=Servicio.nombre == "TINTORERIA",
        options=[joinedload(Servicio.proveedores)],
    ).proveedores

    colores = crud_color.get_multi(session)

    return ProgramacionTintoreriaResponse(
        tejedurias=tejedurias, tintorerias=tintorerias, colores=colores
    )


@router.post("/programacion-tintoreria")
def create_programacion_tintoreria(
    session: SessionDependency, body: ProgramacionTintoreriaCreateSchema
):
    from_tejeduria = crud_proveedor.get_by_pk_or_404(session, body.from_tejeduria_id)
    to_tintoreria = crud_proveedor.get_by_pk_or_404(session, body.to_tintoreria_id)

    programacion_tintoreria = ProgramacionTintoreria(
        from_tejeduria_id=from_tejeduria.proveedor_id,
        to_tintoreria_id=to_tintoreria.proveedor_id,
    )
    # message, _ = crud_programacion_tintoreria.create(session, programacion_tintoreria, commit=False, refresh=True)
    session.add(programacion_tintoreria)
    session.flush()

    # TODO: Validar que el numero de las partidas sean distintas
    # TODO: Validar que hay rollos disponibles
    for partida in body.partidas:
        crud_color.get_by_pk_or_404(session, partida.color_id)
        session.add(
            Partida(
                programacion_tintoreria_id=programacion_tintoreria.programacion_tintoreria_id,
                **partida.model_dump(exclude="detalles"),
            )
        )
        for detalle in partida.detalles:
            suborden = crud_orden_servicio_tejeduria_detalle.get_by_pk_or_404(
                session, detalle.model_dump(exclude={"nro_rollos", "cantidad_kg"})
            )

            current_nro_rollos = (
                suborden.reporte_tejeduria_nro_rollos - detalle.nro_rollos
            )
            current_cantidad_kg = suborden.reporte_tejeduria_cantidad_kg - float(
                detalle.cantidad_kg
            )

            crud_orden_servicio_tejeduria_detalle.update(
                session,
                suborden,
                {
                    "reporte_tejeduria_nro_rollos": current_nro_rollos,
                    "reporte_tejeduria_cantidad_kg": current_cantidad_kg,
                },
                commit=False,
            )
            session.add(
                PartidaDetalle(
                    programacion_tintoreria_id=programacion_tintoreria.programacion_tintoreria_id,
                    nro_partida=partida.nro_partida,
                    **detalle.model_dump(),
                )
            )
    session.commit()
    return {"message": "EPT creada y enviada"}


@router.get(
    "/programacion-tintoreria/{tejeduria_id}/stock",
    response_model=OrdenServicioTejeduriaWithDetallesListSchema,
)
def get_current_stock_by_tejeduria_id(session: SessionDependency, tejeduria_id: str):
    ordenes = crud_orden_servicio_tejeduria.get_multi(
        session,
        filter=and_(
            OrdenServicioTejeduria.tejeduria_id == tejeduria_id,
            OrdenServicioTejeduria.estado == "PENDIENTE",
        ),
        options=[joinedload(OrdenServicioTejeduria.detalles)],
        apply_unique=True,
    )

    return OrdenServicioTejeduriaWithDetallesListSchema(ordenes=ordenes)
