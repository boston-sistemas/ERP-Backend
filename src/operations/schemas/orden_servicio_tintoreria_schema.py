from pydantic import BaseModel

from .orden_servicio_tintoreria_detalle_schema import (
    OrdenServicioTintoreriaDetalleCreateSchema,
    OrdenServicioTintoreriaDetalleCreateSchemaByProgramacion,
)


class OrdenServicioTintoreriaID(BaseModel):
    id: int


class OrdenServicioTintoreriaBase(BaseModel):
    programacion_tintoreria_id: int | None = None
    color_id: int
    estado: str  # TODO: Definir un ENUM
    codigo_mecsa: str | None = None


class OrdenServicioTintoreriaSchema(
    OrdenServicioTintoreriaBase, OrdenServicioTintoreriaID
):
    class Config:
        from_attributes = True


class OrdenServicioTintoreriaCreateSchemaWithDetalle(OrdenServicioTintoreriaBase):
    detalle: list[OrdenServicioTintoreriaDetalleCreateSchema]


class OrdenServicioTintoreriaCreateSchemaWithDetalleByProgramacion(BaseModel):
    color_id: int
    detalle: list[OrdenServicioTintoreriaDetalleCreateSchemaByProgramacion]
