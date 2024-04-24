from fastapi import APIRouter
from sqlmodel import select
from config.database import SessionDependency

from ..models import Usuario

router = APIRouter(tags=["Auth"], prefix="/auth")