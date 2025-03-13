from .email_service import EmailService
from .permission_service import PermissionService

__all__ = ["EmailService", "PermissionService", "AuditService"]


def __getattr__(name):
    if name == "AuditService":
        from .audit_service import AuditService

        return AuditService
    raise AttributeError(f"module {__name__} has no attribute {name}")
