from fastapi import APIRouter
from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from config.database import SessionDependency

from helpers.crud import CRUD
from mecsa_erp.area_operaciones.core.models import Servicio
from mecsa_erp.area_operaciones.modulo0.models import OrdenServicioTejeduria
from mecsa_erp.area_operaciones.modulo0.schemas.orden_servicio_tejeduria import (
    OrdenServicioTejeduriaWithDetallesListSchema,
)
from mecsa_erp.area_operaciones.modulo2.models import Color
from mecsa_erp.area_operaciones.modulo2.schemas import ProgramacionTintoreria
from mecsa_erp.area_operaciones.modulo1.routing import crud_orden_servicio_tejeduria

router = APIRouter(prefix="/operations/v1", tags=["Area Operaciones"])

crud_servicio = CRUD[Servicio, Servicio](Servicio)
crud_color = CRUD[Color, Color](Color)


@router.get("/programacion-tintoreria", response_model=ProgramacionTintoreria)
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

    return ProgramacionTintoreria(
        tejedurias=tejedurias, tintorerias=tintorerias, colores=colores
    )


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
