from typing import Optional
from uuid import UUID
from sqlalchemy import TIMESTAMP, Column, Numeric, func
from sqlmodel import Field, SQLModel
from datetime import datetime

class OrdenServicioTejeduriaDetalleReporteLog(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_detalle_reporte_log"

    log_id: Optional[UUID] = Field(primary_key=True)
    proveedor_id: str
    orden_servicio_tejeduria_id: str
    crudo_id: str
    reporte_tejeduria_nro_rollos: int
    reporte_tejeduria_cantidad_kg: float = Field(sa_type=Numeric)
    timestamp: Optional[datetime] = Field(sa_column=Column(TIMESTAMP, server_default=func.now(), nullable=False))