__all__ = ["EmailService", "PermissionService"]


_module_map = {
    "EmailService": "email_service",
    "PermissionService": "permission_service",
}


def __getattr__(name):
    if name in _module_map:
        module_name = _module_map[name]
        module = __import__(f"{__name__}.{module_name}", fromlist=[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
