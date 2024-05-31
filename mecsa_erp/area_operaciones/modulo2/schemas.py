from sqlmodel import SQLModel

from mecsa_erp.area_operaciones.modulo0.schemas.orden_servicio_tejeduria_detalle import (
    OrdenServicioTejeduriaDetalleSchema,
)


class ProgramacionTintoreria(SQLModel):
    subordenes: list[OrdenServicioTejeduriaDetalleSchema]
