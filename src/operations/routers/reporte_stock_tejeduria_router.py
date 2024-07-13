from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.operations.schemas import (
    OrdenServicioTejeduriaDetalleStockUpdateSchemaList,
    ReporteStockTejeduriaResponse,
)
from src.operations.services import ReporteStockTejeduriaService

router = APIRouter(
    tags=["Area Operaciones - Reporte Stock Tejeduria"], prefix="/reporte-stock"
)


@router.get("/", response_model=ReporteStockTejeduriaResponse)
async def reporte_stock_tejeduria(db: AsyncSession = Depends(get_db)):
    reporte_service = ReporteStockTejeduriaService(db)
    # user_id = token_data.usuario_id
    user_id = 1
    result = await reporte_service.retrieve_ordenes_pendientes_by_tejeduria(user_id)
    if result.is_success:
        return result.value

    raise result.error


@router.put("/subordenes")
async def update_subordenes_stock(
    body: OrdenServicioTejeduriaDetalleStockUpdateSchemaList,
    db: AsyncSession = Depends(get_db),
):
    reporte_service = ReporteStockTejeduriaService(db)
    subordenes = body.subordenes
    update_result = await reporte_service.update_subordenes_stock(subordenes)
    if update_result.is_success:
        if len(subordenes) > 1:
            return {"message": "Suborden de servicio de tejeduría actualizada."}
        return {"message": "Subordenes de servicio de tejeduría actualizadas."}

    raise update_result.error
