from sqlmodel import Field, SQLModel

from mecsa_erp.area_operaciones.core.schemas.proveedor import ProveedorSchema
from mecsa_erp.area_operaciones.modulo2.models import Color


class ProgramacionTintoreriaResponse(SQLModel):
    tejedurias: list[ProveedorSchema]
    tintorerias: list[ProveedorSchema]
    colores: list[Color]


class PartidaDetalleCreateSchema(SQLModel):
    orden_servicio_tejeduria_id: str
    crudo_id: str
    nro_rollos: int = Field(ge=0)
    cantidad_kg: float = Field(ge=0)


class PartidaCreateSchema(SQLModel):
    nro_partida: int
    color_id: int

    detalles: list[PartidaDetalleCreateSchema]


class ProgramacionTintoreriaCreateSchema(SQLModel):
    from_tejeduria_id: str
    to_tintoreria_id: str

    partidas: list[PartidaCreateSchema]
