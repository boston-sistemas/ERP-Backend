from pydantic import BaseModel

from .orden_servicio_tejeduria import (
    OrdenServicioTejeduriaSchema,
    OrdenServicioTejeduriaWithDetallesSchema,
)


class ReporteStock(BaseModel):
    ordenes: list[OrdenServicioTejeduriaWithDetallesSchema]


class RevisionStock(BaseModel):
    ordenes_pendientes: list[OrdenServicioTejeduriaSchema]
    ordenes_cerradas: list[OrdenServicioTejeduriaSchema]
