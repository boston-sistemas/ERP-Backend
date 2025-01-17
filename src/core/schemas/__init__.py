from .abstract_schema import ItemIsUpdatableSchema
from .custom_schema import CustomBaseModel
from .email_schema import EmailAttachmentSchema, EmailSchema

__all__ = [
    "CustomBaseModel",
    "EmailAttachmentSchema",
    "EmailSchema",
    "ItemIsUpdatableSchema",
]
