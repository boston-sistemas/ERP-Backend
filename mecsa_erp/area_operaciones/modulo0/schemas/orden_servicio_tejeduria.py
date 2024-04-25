from sqlmodel import SQLModel

from mecsa_erp.area_operaciones.core.schemas.proveedor import ProveedorSchema

from .orden_servicio_tejeduria_detalle import OrdenServicioTejeduriaDetalleSchema


class OrdenServicioTejeduriaBase(SQLModel):
    orden_servicio_tejeduria_id: str
    tejeduria_id: str
    estado: str


class OrdenServicioTejeduriaSimpleSchema(OrdenServicioTejeduriaBase):
    pass


class OrdenServicioTejeduriaSchema(OrdenServicioTejeduriaBase):
    proveedor: ProveedorSchema
    detalles: list[OrdenServicioTejeduriaDetalleSchema]


class OrdenServicioTejeduriaListSchema(SQLModel):
    data: list[OrdenServicioTejeduriaSchema]
    count: int
