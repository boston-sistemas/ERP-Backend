from fastapi import APIRouter

from src.core.database import SessionDependency
from src.security.schemas import AccesoListSchema
from src.security.services.accesos_services import AccessService

router = APIRouter(tags=["Seguridad - Accesos"], prefix="/accesos")


@router.get("/", response_model=AccesoListSchema)
def list_accesos(session: SessionDependency):
    session = AccessService(session)
    accesos = session.read_access()
    return AccesoListSchema(accesos=accesos)
