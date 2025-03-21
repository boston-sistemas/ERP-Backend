from src.core.exceptions import NotFoundException
from src.core.result import Failure


class AuditFailures:
    AUDIT_ACTION_NOT_FOUND = Failure(
        NotFoundException(
            "El registro de auditoría de acciones de endpoint no fue encontrado"
        )
    )
