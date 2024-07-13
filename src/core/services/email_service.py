import resend
from jinja2 import Environment, FileSystemLoader

from src.core.config import settings

EMAIL_FROM = "practicante.sistemas@boston.com.pe <noreply@boston.com.pe>"
LOGO_MECSA = "https://lh3.googleusercontent.com/pw/AP1GczOxb5h_TPjSWvXctIscyr_Yedt7H2ck4BJMH_8iuedQOxo0g-kRtWkDlJiQuIU6-6zDRaw00vFLTcuMlyi5_uiG17-yiD4WdtOhRs1Q2lunl_sr11qSdsK5fozwLoxaANW2ycTRPjVZPW8e3KsV27s=w1920-h610-s-no-gm"


class EmailService:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY
        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=settings.ASSETS_DIR + "email_templates")
        )

    async def send_email(
        self, email_from: str, email_to: list[str], subject: str, html_content: str
    ) -> dict:
        params = {
            "from": email_from,
            "to": email_to,
            "subject": subject,
            "html": html_content,
        }
        email = resend.Emails.send(params)
        return email

    async def send_welcome_email(
        self, email_to: str, name: str, username: str, password: str
    ):
        subject = "Bienvenido a MECSA"
        template = self.template_env.get_template("send_welcome_email.html")
        html_content = template.render(
            LOGO_MECSA=LOGO_MECSA,
            name=name,
            username=username,
            password=password,
            FRONTEND_URL=settings.FRONTEND_URL,
        )
        await self.send_email(EMAIL_FROM, [email_to], subject, html_content)

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

        await self.send_email(EMAIL_FROM, [email_to], subject, html_content)
