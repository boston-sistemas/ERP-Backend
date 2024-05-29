from sqlmodel import SQLModel

from mecsa_erp.area_operaciones.modulo0.schemas.orden_servicio_tejeduria import (
    OrdenServicioTejeduriaSchema,
)


class ReporteStock(SQLModel):
    ordenes: list[OrdenServicioTejeduriaSchema]


class RevisionStock(SQLModel):
    ordenes_pendientes: list[OrdenServicioTejeduriaSchema]
    ordenes_cerradas: list[OrdenServicioTejeduriaSchema]
