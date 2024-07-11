from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from .orden_servicio_tejeduria_detalle_schema import OrdenServicioTejeduriaDetalleSchema
from .proveedor_schema import ProveedorSchema


class OrdenServicioTejeduriaIDSchema(BaseModel):
    orden_servicio_tejeduria_id: str


class OrdenServicioTejeduriaBase(BaseModel):
    orden_servicio_tejeduria_id: str
    tejeduria_id: str
    fecha: datetime
    estado: str

    class Config:
        from_attributes = True


class OrdenServicioTejeduriaSimpleSchema(OrdenServicioTejeduriaBase):
    pass


class OrdenServicioTejeduriaSchema(OrdenServicioTejeduriaBase):
    proveedor: ProveedorSchema
    detalles: list[OrdenServicioTejeduriaDetalleSchema]


class OrdenServicioTejeduriaWithDetallesSchema(OrdenServicioTejeduriaBase):
    detalles: list[OrdenServicioTejeduriaDetalleSchema]


class OrdenServicioTejeduriaWithDetallesListSchema(BaseModel):
    ordenes: list[OrdenServicioTejeduriaWithDetallesSchema]


class OrdenServicioTejeduriaEstadoEnum(str, Enum):
    pendiente = "PENDIENTE"
    cerrado = "CERRADO"
    liquidado = "LIQUIDADO"


class OrdenServicioTejeduriaUpdateSchema(BaseModel):
    estado: OrdenServicioTejeduriaEstadoEnum


class OrdenServicioTejeduriaUpdateSchemaByID(
    OrdenServicioTejeduriaUpdateSchema, OrdenServicioTejeduriaIDSchema
):
    pass


class OrdenServicioTejeduriaListUpdateSchema(BaseModel):
    ordenes: list[OrdenServicioTejeduriaUpdateSchemaByID]
