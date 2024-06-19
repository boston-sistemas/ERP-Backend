from sqlmodel import SQLModel

from src.operations.models import Color

from .partida import PartidaCreateSchema
from .proveedor import ProveedorSchema


class ProgramacionTintoreriaResponse(SQLModel):
    tejedurias: list[ProveedorSchema]
    tintorerias: list[ProveedorSchema]
    colores: list[Color]


class ProgramacionTintoreriaCreateSchema(SQLModel):
    from_tejeduria_id: str
    to_tintoreria_id: str

    partidas: list[PartidaCreateSchema]
