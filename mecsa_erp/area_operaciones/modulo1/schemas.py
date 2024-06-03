from sqlmodel import SQLModel

from mecsa_erp.area_operaciones.modulo0.schemas.orden_servicio_tejeduria import (
    OrdenServicioTejeduriaSchema,
)
from mecsa_erp.area_operaciones.modulo0.schemas.orden_servicio_tejeduria_detalle import (
    OrdenServicioTejeduriaDetalleSchema,
)


class ReporteStock(SQLModel):
    subordenes: list[OrdenServicioTejeduriaDetalleSchema]


class RevisionStock(SQLModel):
    ordenes_pendientes: list[OrdenServicioTejeduriaSchema]
    ordenes_cerradas: list[OrdenServicioTejeduriaSchema]
