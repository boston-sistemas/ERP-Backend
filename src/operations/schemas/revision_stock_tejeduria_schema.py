from pydantic import BaseModel

from .orden_servicio_tejeduria import OrdenServicioTejeduriaSchema


class RevisionStockTejeduriaResponse(BaseModel):
    ordenes_pendientes: list[OrdenServicioTejeduriaSchema]
    ordenes_cerradas: list[OrdenServicioTejeduriaSchema]
