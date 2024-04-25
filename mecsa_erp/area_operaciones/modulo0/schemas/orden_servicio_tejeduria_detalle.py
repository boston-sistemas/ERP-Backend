from sqlmodel import SQLModel
from decimal import Decimal


class OrdenServicioTejeduriaDetalleBase(SQLModel):
    orden_servicio_tejeduria_id: str
    crudo_id: str
    cantidad_kg: Decimal
    es_complemento: bool
    estado: str
    reporte_tejeduria_nro_rollos: int
    reporte_tejeduria_cantidad_kg: Decimal


class OrdenServicioTejeduriaDetalleSchema(OrdenServicioTejeduriaDetalleBase):
    pass
