from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_promec_db

router = APIRouter(
    tags=["Ordenes de Compra"],
    prefix="/orden_compra"
)

@router.get("/")
