from core.crud import CRUD

from operations.models import (
    Color,
    OrdenServicioTejeduria,
    OrdenServicioTejeduriaDetalle,
    ProgramacionTintoreria,
    Proveedor,
    Servicio,
)

crud_orden_servicio_tejeduria = CRUD[OrdenServicioTejeduria, OrdenServicioTejeduria](
    OrdenServicioTejeduria
)

crud_orden_servicio_tejeduria_detalle = CRUD[
    OrdenServicioTejeduriaDetalle, OrdenServicioTejeduriaDetalle
](OrdenServicioTejeduriaDetalle)

crud_servicio = CRUD[Servicio, Servicio](Servicio)

crud_color = CRUD[Color, Color](Color)

crud_programacion_tintoreria = CRUD[ProgramacionTintoreria, ProgramacionTintoreria](
    ProgramacionTintoreria
)

crud_proveedor = CRUD[Proveedor, Proveedor](Proveedor)
