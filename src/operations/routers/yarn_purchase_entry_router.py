from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_promec_db


router = APIRouter()

# @router.get("/")
