from .card_operation_service import CardOperationService
from .color_service import ColorService
from .dyeing_service_dispatch_service import DyeingServiceDispatchService
from .especialidad_empresa_service import EspecialidadEmpresaService
from .fabric_service import FabricService
from .fiber_service import FiberService
from .mecsa_color_service import MecsaColorService
from .orden_compra_service import OrdenCompraService
from .orden_servicio_tejeduria_detalle_service import (
    OrdenServicioTejeduriaDetalleService,
)
from .orden_servicio_tejeduria_service import OrdenServicioTejeduriaService
from .orden_servicio_tintoreria_detalle_service import (
    OrdenServicioTintoreriaDetalleService,
)
from .orden_servicio_tintoreria_service import OrdenServicioTintoreriaService
from .programacion_tintoreria_service import ProgramacionTintoreriaService
from .proveedor_service import ProveedorService
from .reporte_stock_tejeduria_service import ReporteStockTejeduriaService
from .revision_stock_tejeduria_service import RevisionStockTejeduriaService
from .series_service import BarcodeSeries, SeriesService, YarnPurchaseEntrySeries
from .unit_service import UnitService
from .yarn_purchase_entry_detail_heavy_service import (
    YarnPurchaseEntryDetailHeavyService,
)
from .yarn_service import YarnService

__all__ = [
    "FabricService",
    "BarcodeSeries",
    "SeriesService",
    "YarnService",
    "UnitService",
    "FiberService",
    "OrdenServicioTintoreriaDetalleService",
    "OrdenServicioTintoreriaService",
    "OrdenServicioTejeduriaService",
    "OrdenServicioTejeduriaDetalleService",
    "ReporteStockTejeduriaService",
    "RevisionStockTejeduriaService",
    "ColorService",
    "EspecialidadEmpresaService",
    "ProveedorService",
    "ProgramacionTintoreriaService",
    "MecsaColorService",
    "OrdenCompraService",
    "YarnPurchaseEntryService",
    "YarnPurchaseEntrySeries",
    "YarnWeavingDispatchService",
    "YarnPurchaseEntryDetailHeavyService",
    "ServiceOrderService",
    "WeavingServiceEntryService",
    "DyeingServiceDispatchService",
    "CardOperationService",
]

_module_map = {
    "ServiceOrderService": "service_order_service",
    "WeavingServiceEntryService": "weaving_service_entry_service",
    "YarnPurchaseEntryService": "yarn_purchase_entry_service",
    "YarnWeavingDispatchService": "yarn_weaving_dispatch_service",
}


def __getattr__(name):
    if name in _module_map:
        module_name = _module_map[name]
        module = __import__(f"{__name__}.{module_name}", fromlist=[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
