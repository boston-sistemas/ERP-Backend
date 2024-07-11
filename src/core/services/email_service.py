import os
import resend
from typing import List
from jinja2 import Environment, FileSystemLoader

URL_ERP_MECSA = "http://localhost:3000"
EMAIL_FROM = "practicante.sistemas@boston.com.pe"
LOGO_MECSA_PNG = "http://localhost:8000/public/logo-mecsa-negro.png"

template_loader = FileSystemLoader(searchpath="./resend_html")
template_env = Environment(loader=template_loader)

class EmailService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        resend.api_key = self.api_key

    async def send_email(self, email_from: str, email_to: List[str], subject: str, html_content: str) -> dict:
        params = {
            "from": email_from,
            "to": email_to,
            "subject": subject,
            "html": html_content,
        }
        email = resend.Emails.send(params)
        return email

    async def send_welcome_email(self, email_to: str, name: str, username: str, password: str):
        subject = "Bienvenido a MECSA"
        template = template_env.get_template("send_welcome_email.html")
        html_content = template.render(
            LOGO_MECSA_PNG=LOGO_MECSA_PNG,
            name=name,
            username=username,
            password=password,
            URL_ERP_MECSA=URL_ERP_MECSA
        )
        await self.send_email(EMAIL_FROM, [email_to], subject, html_content)

    async def send_auth_token_email(self, email_to: str, username: str, token: str):
        subject = "Tu Token de Autenticación"
        template = template_env.get_template("send_auth_token_email.html")
        html_content = template.render(
            LOGO_MECSA_PNG=LOGO_MECSA_PNG,
            username=username,
            token=token,
            URL_ERP_MECSA=URL_ERP_MECSA
        )
        await self.send_email(EMAIL_FROM, [email_to], subject, html_content)