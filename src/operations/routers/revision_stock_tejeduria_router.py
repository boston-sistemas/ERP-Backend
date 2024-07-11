from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.operations.schemas import (
    OrdenServicioTejeduriaListUpdateSchema,
    RevisionStockTejeduriaResponse,
)
from src.operations.services import RevisionStockTejeduriaService

router = APIRouter(
    tags=["Area Operaciones - Revisión Stock Tejeduria"], prefix="/revision-stock"
)


@router.get("/", response_model=RevisionStockTejeduriaResponse)
async def revision_stock(db: AsyncSession = Depends(get_db)):
    revision_service = RevisionStockTejeduriaService(db)
    return await revision_service.retrieve_ordenes_pendientes_and_cerradas()


@router.put("/ordenes")
async def update_ordenes_estado(
    body: OrdenServicioTejeduriaListUpdateSchema, db: AsyncSession = Depends(get_db)
):
    revision_service = RevisionStockTejeduriaService(db)
    ordenes = body.ordenes
    update_result = await revision_service.update_ordenes_estado(ordenes)
    if update_result.is_success:
        if len(ordenes) > 1:
            return {"message": "Ordenes de servicio de tejeduría actualizadas."}
        return {"message": "Orden de servicio de tejeduría actualizada."}

    raise update_result.error
