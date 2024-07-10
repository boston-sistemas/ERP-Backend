from pydantic import BaseModel

from .color_schema import ColorSchema
from .proveedor_schema import ProveedorSchema


class ProgramacionTintoreriaParametersResponse(BaseModel):
    tejedurias: list[ProveedorSchema]
    tintorerias: list[ProveedorSchema]
    colores: list[ColorSchema]
