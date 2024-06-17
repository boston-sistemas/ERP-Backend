from core.database import SessionDependency
from fastapi import APIRouter

from security.cruds import crud_acceso
from security.schemas import AccesoListSchema

router = APIRouter(tags=["Seguridad - Accesos"], prefix="/accesos")


@router.get("/", response_model=AccesoListSchema)
def list_accesos(session: SessionDependency):
    accesos = crud_acceso.get_multi(session)
    return AccesoListSchema(accesos=accesos)
