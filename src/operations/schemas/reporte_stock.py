from sqlmodel import SQLModel

from operations.schemas.orden_servicio_tejeduria import (
    OrdenServicioTejeduriaSchema,
    OrdenServicioTejeduriaWithDetallesSchema,
)


class ReporteStock(SQLModel):
    ordenes: list[OrdenServicioTejeduriaWithDetallesSchema]


class RevisionStock(SQLModel):
    ordenes_pendientes: list[OrdenServicioTejeduriaSchema]
    ordenes_cerradas: list[OrdenServicioTejeduriaSchema]
