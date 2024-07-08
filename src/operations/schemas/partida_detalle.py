from pydantic import BaseModel, Field


class PartidaDetalleCreateSchema(BaseModel):
    orden_servicio_tejeduria_id: str
    crudo_id: str
    nro_rollos: int = Field(ge=0)
    cantidad_kg: float = Field(ge=0)
