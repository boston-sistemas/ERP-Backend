from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.operations.schemas import MovimientoIngresoCrudoListCreateSchema
from src.operations.services import MovimientoIngresoCrudoService

router = APIRouter(
    tags=["Area Operaciones - Movimiento Ingreso Crudo"],
    prefix="/movimiento-ingreso-crudo",
)


@router.post("/")
async def create_movimientos(
    body: MovimientoIngresoCrudoListCreateSchema, db: AsyncSession = Depends(get_db)
):
    service = MovimientoIngresoCrudoService(db)
    await service.create_movimientos(body.movimientos)
