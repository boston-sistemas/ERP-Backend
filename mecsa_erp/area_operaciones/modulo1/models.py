from sqlalchemy import TIMESTAMP, Column, Numeric, func
from sqlmodel import SQLModel, Field

from datetime import datetime
from decimal import Decimal
from uuid import UUID


class OrdenServicioTejeduriaDetalleReporteLog(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_detalle_reporte_log"

    log_id: UUID = Field(primary_key=True)
    proveedor_id: str
    orden_servicio_tejeduria_id: str
    crudo_id: str
    estado: str
    reporte_tejeduria_nro_rollos: int
    reporte_tejeduria_cantidad_kg: Decimal = Field(sa_type=Numeric)
    timestamp: datetime = Field(sa_column=Column(TIMESTAMP, server_default=func.now()))
