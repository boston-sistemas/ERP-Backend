from pydantic import EmailStr

from .custom_schema import CustomBaseModel


class EmailAttachmentSchema(CustomBaseModel):
    filename: str
    content: str | bytes
    content_type: str


class EmailSchema(CustomBaseModel):
    from_: str
    to: list[EmailStr]
    cc: list[EmailStr] | None = None
    bcc: list[EmailStr] | None = None
    subject: str
    body_text: str | None = None
    body_html: str | None = None
    attachments: list[EmailAttachmentSchema] = []
