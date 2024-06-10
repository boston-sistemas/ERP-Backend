from sqlalchemy import TIMESTAMP, Column, String, func
from sqlmodel import SQLModel, Field

from datetime import datetime
from uuid import UUID

from mecsa_erp.area_operaciones.constants import (
    MAX_LENGTH_CRUDO_ID,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID,
    MAX_LENGTH_PROVEEDOR_ID,
)


class OrdenServicioTejeduriaDetalleReporteLog(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_detalle_reporte_log"

    log_id: UUID = Field(primary_key=True)
    proveedor_id: str = Field(sa_type=String(length=MAX_LENGTH_PROVEEDOR_ID))
    orden_servicio_tejeduria_id: str = Field(
        sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: str = Field(sa_type=String(length=MAX_LENGTH_CRUDO_ID))
    estado: str = Field(
        sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO)
    )
    reporte_tejeduria_nro_rollos: int
    reporte_tejeduria_cantidad_kg: float
    timestamp: datetime = Field(sa_column=Column(TIMESTAMP, server_default=func.now()))
