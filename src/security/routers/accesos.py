from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.schemas import AccesoListSchema
from src.security.services.accesos_services import AccessService

router = APIRouter(tags=["Seguridad - Accesos"], prefix="/accesos")


@router.get("/", response_model=AccesoListSchema)
async def list_accesos(db: AsyncSession = Depends(get_db)) -> AccesoListSchema:
    session = AccessService(db)
    accesos = await session.read_access()
    return AccesoListSchema(accesos=accesos)
