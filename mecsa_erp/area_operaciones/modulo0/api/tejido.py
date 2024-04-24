from fastapi import APIRouter
from sqlmodel import select
from config.database import SessionDependency

from ..models import Tejido

router = APIRouter(tags=["Modulo 0 - Tejido"], prefix="/tejido")

@router.get(path="/", name="Listar Tejidos")
def get_tejido(session: SessionDependency):
    statement = select(Tejido)
    items = session.exec(statement).all()
    return items