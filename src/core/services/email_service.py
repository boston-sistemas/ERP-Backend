import base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import aiosmtplib
import resend
from jinja2 import Environment, FileSystemLoader

from src.core.config import settings
from src.core.constants import LOGO_MECSA, AppEnvironment
from src.core.schemas import EmailAttachmentSchema, EmailSchema
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.models import Proveedor
from src.operations.utils.programacion_tintoreria import generate_html


class EmailService:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY
        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=settings.ASSETS_DIR + "email_templates")
        )

    async def send_email(self, email: EmailSchema) -> dict:
        if settings.ENVIRONMENT == AppEnvironment.PRODUCTION:
            params: resend.Emails.SendParams = {
                "from": email.from_,
                "to": email.to,
                "subject": email.subject,
            }

            if email.cc:
                params["cc"] = email.cc
            if email.bcc:
                params["bcc"] = email.bcc
            if email.body_text:
                params["text"] = email.body_text
            if email.body_html:
                params["html"] = email.body_html
            if email.attachments:
                params["attachments"] = [
                    {
                        "filename": attachment.filename,
                        "content": base64.b64encode(attachment.content).decode("utf-8")
                        if isinstance(attachment.content, bytes)
                        else attachment.content,
                        "content_type": attachment.content_type,
                    }
                    for attachment in email.attachments
                ]

            email = resend.Emails.send(params)
            return email

        else:
            message = MIMEMultipart()
            message["From"] = email.from_
            message["To"] = ", ".join(email.to)
            message["Subject"] = email.subject

            if email.cc:
                message["Cc"] = ", ".join(email.cc)
            if email.bcc:
                message["Bcc"] = ", ".join(email.bcc)
            if email.body_text:
                message.attach(MIMEText(email.body_text, "plain"))
            if email.body_html:
                message.attach(MIMEText(email.body_html, "html"))

            for attachment in email.attachments:
                part = MIMEApplication(attachment.content, Name=attachment.filename)
                part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=("utf-8", "", attachment.filename),
                )
                part.add_header("Content-Type", attachment.content_type)
                message.attach(part)

            recipients = email.to + (email.cc or []) + (email.bcc or [])
            await aiosmtplib.send(
                message,
                recipients=recipients,
                hostname=settings.MAILHOG_HOSTNAME,
                port=settings.MAILHOG_PORT,
            )

    async def send_programacion_tintoreria_email(
        self,
        encoded_pdf: bytes,
        tejeduria: Proveedor,
        tintoreria: Proveedor,
        data: list,
        email_from: str,
        email_to: list[str],
    ):
        template = self.template_env.get_template("send_programming_dry_cleaners.html")
        html_content = generate_html(tejeduria, tintoreria, data, template)

        current_week: int = calculate_time(timezone=PERU_TIMEZONE).isocalendar()[1]
        subject = "PROGRAMACIÓN TINTORERÍA - SEMANA " + str(current_week)

        await self.send_email(
            EmailSchema(
                from_=formataddr((settings.SENDER_NAME, settings.SENDER_EMAIL)),
                to=email_to,
                subject=subject,
                body_html=html_content,
                attachments=[
                    EmailAttachmentSchema(
                        filename="reporte.pdf",
                        content=encoded_pdf,
                        content_type="application/pdf",
                    )
                ],
            )
        )

    async def send_welcome_email(
        self, email_to: str, display_name: str, username: str, password: str
    ):
        subject = "Bienvenido al Portal de MECSA"
        template = self.template_env.get_template("send_welcome_email.html")
        html_content = template.render(
            LOGO_MECSA=LOGO_MECSA,
            display_name=display_name,
            username=username,
            password=password,
            FRONTEND_URL=settings.FRONTEND_URL,
        )

        await self.send_email(
            EmailSchema(
                from_=formataddr((settings.SENDER_NAME, settings.SENDER_EMAIL)),
                to=[email_to],
                subject=subject,
                body_html=html_content,
            )
        )

    async def send_auth_token_email(
        self, email_to: str, username: str, token: str, expiration_at: str
    ):
        subject = "Codigo de Acceso - SISTEMAS MECSA"
        template = self.template_env.get_template("send_auth_token_email.html")
        html_content = template.render(
            LOGO_MECSA=LOGO_MECSA,
            username=username,
            token=token,
            expiration_at=expiration_at,
        )

        await self.send_email(
            EmailSchema(
                from_=formataddr((settings.SENDER_NAME, settings.SENDER_EMAIL)),
                to=[email_to],
                subject=subject,
                body_html=html_content,
            )
        )

    async def send_reset_password_email(
        self, email_to: str, display_name: str, username: str, password: str
    ):
        subject = "Nueva Contraseña - SISTEMAS MECSA"
        template = self.template_env.get_template("send_reset_password_email.html")
        html_content = template.render(
            LOGO_MECSA=LOGO_MECSA,
            display_name=display_name,
            username=username,
            password=password,
            FRONTEND_URL=settings.FRONTEND_URL,
        )

        await self.send_email(
            EmailSchema(
                from_=formataddr((settings.SENDER_NAME, settings.SENDER_EMAIL)),
                to=[email_to],
                subject=subject,
                body_html=html_content,
            )
        )
