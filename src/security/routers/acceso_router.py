from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.schemas import AccesoListSchema, AccesoSchema, AccessCreateSchema
from src.security.services import AccesoService

router = APIRouter(tags=["Seguridad - Accesos"], prefix="/accesos")


@router.get("/", response_model=AccesoListSchema)
async def read_accesos(db: AsyncSession = Depends(get_db)) -> AccesoListSchema:
    acceso_service = AccesoService(db)

    accesos = await acceso_service.read_accesos()

    return AccesoListSchema(accesos=accesos)


@router.post("/", response_model=AccesoSchema)
async def create_access(form: AccessCreateSchema, db: AsyncSession = Depends(get_db)):
    access_service = AccesoService(db)

    result = await access_service.create_access(form)

    if result.is_success:
        return result.value

    raise result.error
