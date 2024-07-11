from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.operations.schemas import (
    ProgramacionTintoreriaParametersResponse,
)
from src.operations.services import ProgramacionTintoreriaService

router = APIRouter(
    tags=["Area Operaciones - Programacion de Tintoreria"],
    prefix="/programacion-tintoreria",
)


@router.get("/parametros", response_model=ProgramacionTintoreriaParametersResponse)
async def retrieve_parameters(db: AsyncSession = Depends(get_db)):
    programacion_tintoreria = ProgramacionTintoreriaService(db)
    result = await programacion_tintoreria.retrieve_parameters()
    if result.is_success:
        return result.value

    raise result.error
