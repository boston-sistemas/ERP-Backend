from sqlmodel import SQLModel

from mecsa_erp.area_operaciones.core.schemas.proveedor import ProveedorSchema
from mecsa_erp.area_operaciones.modulo2.models import Color


class ProgramacionTintoreria(SQLModel):
    tejedurias: list[ProveedorSchema]
    tintorerias: list[ProveedorSchema]
    colores: list[Color]
