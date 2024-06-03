from datetime import datetime
from sqlmodel import SQLModel

from mecsa_erp.area_operaciones.core.schemas.proveedor import ProveedorSchema

from .orden_servicio_tejeduria_detalle import OrdenServicioTejeduriaDetalleSchema


class OrdenServicioTejeduriaBase(SQLModel):
    tejeduria_id: str
    orden_servicio_tejeduria_id: str
    fecha: datetime
    estado: str


class OrdenServicioTejeduriaSimpleSchema(OrdenServicioTejeduriaBase):
    pass

class OrdenServicioTejeduriaSchema(OrdenServicioTejeduriaBase):
    proveedor: ProveedorSchema
    detalles: list[OrdenServicioTejeduriaDetalleSchema]


class OrdenServicioTejeduriaSimpleListSchema(SQLModel):
    data: list[OrdenServicioTejeduriaSimpleSchema]
    count: int = None


class OrdenServicioTejeduriaListSchema(SQLModel):
    data: list[OrdenServicioTejeduriaSchema]
    count: int = None


class OrdenServicioTejeduriaUpdateSchema(SQLModel):
    estado: str


class OrdenServicioTejeduriaUpdateMultipleSchema(SQLModel):
    data: list[OrdenServicioTejeduriaBase]
