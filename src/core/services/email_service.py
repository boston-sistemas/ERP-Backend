import os
import resend
from typing import List
from jinja2 import Environment, FileSystemLoader

URL_ERP_MECSA = "http://localhost:3000"
EMAIL_FROM = "practicante.sistemas@boston.com.pe <noreply@boston.com.pe>"
LOGO_MECSA= "https://lh3.googleusercontent.com/pw/AP1GczOxb5h_TPjSWvXctIscyr_Yedt7H2ck4BJMH_8iuedQOxo0g-kRtWkDlJiQuIU6-6zDRaw00vFLTcuMlyi5_uiG17-yiD4WdtOhRs1Q2lunl_sr11qSdsK5fozwLoxaANW2ycTRPjVZPW8e3KsV27s=w1920-h610-s-no-gm"
template_loader = FileSystemLoader(searchpath=os.path.join(os.path.dirname(__file__), "resend_html"))
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
            LOGO_MECSA=LOGO_MECSA,
            name=name,
            username=username,
            password=password,
            URL_ERP_MECSA=URL_ERP_MECSA
        )
        await self.send_email(EMAIL_FROM, [email_to], subject, html_content)

    async def send_auth_token_email(self, email_to: str, username: str, token: str, expiration_at: str):
        subject = "Codigo de Acceso - SISTEMAS MECSA"
        template = template_env.get_template("send_auth_token_email.html")
        html_content = template.render(
            LOGO_MECSA=LOGO_MECSA,
            username=username,
            token=token,
            URL_ERP_MECSA=URL_ERP_MECSA,
            expiration_at= expiration_at
        )
        await self.send_email(EMAIL_FROM, [email_to], subject, html_content)