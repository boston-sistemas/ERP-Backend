from .color_failures import ColorFailures
from .especialidad_empresa_failures import EspecialidadEmpresaFailures
from .orden_servicio_tejeduria_detalle_failures import (
    OrdenServicioTejeduriaDetalleFailures,
)
from .orden_servicio_tejeduria_failures import OrdenServicioTejeduriaFailures
from .orden_servicio_tintoreria_failures import OrdenServicioTintoreriaFailures
from .proveedor_failures import ProveedorFailures
from .reporte_stock_tejeduria_failures import ReporteStockTejeduriaFailures

__all__ = [
    "OrdenServicioTejeduriaFailures",
    "OrdenServicioTejeduriaDetalleFailures",
    "ReporteStockTejeduriaFailures",
    "EspecialidadEmpresaFailures",
    "ProveedorFailures",
    "ColorFailures",
    "OrdenServicioTintoreriaFailures",
]
