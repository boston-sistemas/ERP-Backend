from pydantic import BaseModel

from .color_schema import ColorSchema
from .orden_servicio_tintoreria_schema import (
    OrdenServicioTintoreriaCreateSchemaWithDetalleByProgramacion,
)
from .proveedor_schema import ProveedorSchema


class ProgramacionTintoreriaParametersResponse(BaseModel):
    tejedurias: list[ProveedorSchema]
    tintorerias: list[ProveedorSchema]
    colores: list[ColorSchema]


class ProgramacionTintoreriaCreateSchema(BaseModel):
    from_tejeduria_id: str
    to_tintoreria_id: str

    partidas: list[OrdenServicioTintoreriaCreateSchemaWithDetalleByProgramacion]
