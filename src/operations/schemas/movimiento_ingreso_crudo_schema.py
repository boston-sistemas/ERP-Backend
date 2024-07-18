from pydantic import BaseModel

from .orden_servicio_tejeduria_detalle_schema import (
    OrdenServicioTejeduriaDetalleIDSchema,
)


class MovimientoIngresoCrudoCreateSchema(OrdenServicioTejeduriaDetalleIDSchema):
    nro_rollos: int
    cantidad_kg: float


class MovimientoIngresoCrudoListCreateSchema(BaseModel):
    movimientos: list[MovimientoIngresoCrudoCreateSchema]
