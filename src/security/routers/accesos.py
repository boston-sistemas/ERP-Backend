from fastapi import APIRouter

from src.core.database import SessionDependency
from src.security.cruds import crud_acceso
from src.security.schemas import AccesoListSchema

router = APIRouter(tags=["Seguridad - Accesos"], prefix="/accesos")


@router.get("/", response_model=AccesoListSchema)
def list_accesos(session: SessionDependency):
    accesos = crud_acceso.get_multi(session)
    return AccesoListSchema(accesos=accesos)
