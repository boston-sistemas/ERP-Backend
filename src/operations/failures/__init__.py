from .color_failures import ColorFailures
from .especialidad_empresa_failures import EspecialidadEmpresaFailures
from .fiber_failure import (
    COLOR_DISABLED_WHEN_CREATING_FIBER_FAILURE,
    COLOR_NOT_FOUND_WHEN_CREATING_FIBER_FAILURE,
    FIBER_ALREADY_EXISTS_FAILURE,
    FIBER_CATEGORY_DISABLED_WHEN_CREATING_FIBER_FAILURE,
    FIBER_CATEGORY_NOT_FOUND_WHEN_CREATING_FIBER_FAILURE,
    FIBER_NOT_FOUND_FAILURE,
)
from .mecsa_color_failure import (
    MECSA_COLOR_NAME_ALREADY_EXISTS_FAILURE,
    MECSA_COLOR_NOT_FOUND_FAILURE,
    MECSA_COLOR_SKU_ALREADY_EXISTS_FAILURE,
)
from .orden_servicio_tejeduria_detalle_failures import (
    OrdenServicioTejeduriaDetalleFailures,
)
from .orden_servicio_tejeduria_failures import OrdenServicioTejeduriaFailures
from .orden_servicio_tintoreria_failures import OrdenServicioTintoreriaFailures
from .proveedor_failures import ProveedorFailures
from .reporte_stock_tejeduria_failures import ReporteStockTejeduriaFailures

__all__ = [
    "FIBER_ALREADY_EXISTS_FAILURE",
    "COLOR_NOT_FOUND_WHEN_CREATING_FIBER_FAILURE",
    "COLOR_DISABLED_WHEN_CREATING_FIBER_FAILURE",
    "FIBER_CATEGORY_DISABLED_WHEN_CREATING_FIBER_FAILURE",
    "FIBER_CATEGORY_NOT_FOUND_WHEN_CREATING_FIBER_FAILURE",
    "FIBER_NOT_FOUND_FAILURE",
    "MECSA_COLOR_NAME_ALREADY_EXISTS_FAILURE",
    "MECSA_COLOR_NOT_FOUND_FAILURE",
    "MECSA_COLOR_SKU_ALREADY_EXISTS_FAILURE",
    "OrdenServicioTejeduriaFailures",
    "OrdenServicioTejeduriaDetalleFailures",
    "ReporteStockTejeduriaFailures",
    "EspecialidadEmpresaFailures",
    "ProveedorFailures",
    "ColorFailures",
    "OrdenServicioTintoreriaFailures",
]
