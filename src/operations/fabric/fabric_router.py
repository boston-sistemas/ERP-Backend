from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.schemas import ItemStatusUpdateSchema

from .fabric_service import FabricService
from .finished_fabric import FinishedFabricRouter
from .raw_fabric import RawFabricRouter

router = APIRouter()

router.include_router(
    router=RawFabricRouter,
    prefix="/raw",
)
router.include_router(
    router=FinishedFabricRouter,
    prefix="/finished",
)


@router.put("/{fabric_id}/status")
async def update_fabric_status(
    fabric_id: str,
    form: ItemStatusUpdateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FabricService(db=db, promec_db=promec_db)
    is_active = form.is_active
    result = await service.update_status(fabric_id=fabric_id, is_active=is_active)

    if result.is_success:
        msg = f"El tejido ha sido {'' if is_active else 'des'}activado con éxito"
        return {"message": msg}

    raise result.error
