from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.operations.schemas import (
    ProgramacionTintoreriaCreateSchema,
    ProgramacionTintoreriaParametersResponse,
)
from src.operations.services import ProgramacionTintoreriaService

router = APIRouter(
    tags=["Area Operaciones - Programacion de Tintoreria"],
    prefix="/programacion-tintoreria",
)


@router.get("/parametros", response_model=ProgramacionTintoreriaParametersResponse)
async def retrieve_parameters(db: AsyncSession = Depends(get_db)):
    programacion_service = ProgramacionTintoreriaService(db)
    result = await programacion_service.retrieve_parameters()
    if result.is_success:
        return result.value

    raise result.error


@router.post("/")
async def create_programacion_tintoreria(
    programacion: ProgramacionTintoreriaCreateSchema, db: AsyncSession = Depends(get_db)
):
    programacion_service = ProgramacionTintoreriaService(db)
    creation_result = await programacion_service.create_programacion(programacion)
    if creation_result.is_success:
        return {"message": "Programacion de tintorería hecha y enviada."}

    raise creation_result.error
