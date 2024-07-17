import base64
import uuid
from datetime import datetime

import pytz
import resend
from jinja2 import Environment, FileSystemLoader
from reportlab.lib.pagesizes import landscape, letter

from src.core.config import settings
from src.core.services.pdf_service import PDFService, TableStyle, colors, inch

timezone = pytz.timezone("America/Lima")

LOGO_MECSA = "https://lh3.googleusercontent.com/pw/AP1GczOxb5h_TPjSWvXctIscyr_Yedt7H2ck4BJMH_8iuedQOxo0g-kRtWkDlJiQuIU6-6zDRaw00vFLTcuMlyi5_uiG17-yiD4WdtOhRs1Q2lunl_sr11qSdsK5fozwLoxaANW2ycTRPjVZPW8e3KsV27s=w1920-h610-s-no-gm"

PROGRAMACION_TINTORERIA_ASUNTO = "Fwd: PROGRAMACIÓN TINTORERÍA - SEMANA {0}"
PROGRAMACION_TINTORERIA_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');

        body {{
            font-family: 'Nunito', sans-serif;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            border: 1px solid black;
            padding: 8px;
            text-align: center;
        }}

        th {{
            background-color: #FFCC00;
            font-weight: bold;
            text-align: center;
        }}

        .header-row {{
            background-color: #FFCC00;
            text-align: center;
        }}

        .partida-cell {{
            font-weight: bold;
        }}

        .number-cell {{
            text-align: center;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <p> Buenos días, {0} <p>
    <p>Por favor preparar la siguiente relación de tejido para su despacho, recoge Color y Textura<p>
    <p>Muchas gracias<p>
    <strong>Area de Operaciones</strong>
    <p><strong>Fecha: </strong>{1}<p>
    <table>
        <thead>
            <tr class="header-row">
                {2}
            </tr>
        </thead>
        <tbody>
            {3}
            <tr style="background-color: #111;">
                <td colspan="6" style="text-align: center; font-weight: bold; color: white;">Totales</td>
                <td style="text-align: center; font-weight: bold; color: white;">{4}</td>
                <td style="text-align: center; font-weight: bold; color: white;">{5}</td>
                <td colspan="2" style="color: white;"></td>
            </tr>
        </tbody>
    </table>
</body>
</html>
"""


class EmailService:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY
        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=settings.ASSETS_DIR + "email_templates")
        )
        self.pdf_service = PDFService()

    @staticmethod
    def data_processing(data: dict, lengths: dict, style: TableStyle):
        colWidths = []
        total_rolls = 0
        total_weight = 0
        usable_width = lengths["usable_width"]
        cell = lengths["cell"]

        titles_pdf = [
            title for title in data["title"] if title not in data["ignore_columns_pdf"]
        ]
        index_ignore = [
            index
            for index, title in enumerate(data["title"])
            if title in data["ignore_columns_pdf"]
        ]
        titles_email = "".join(
            f'<th style="text-align: center;">{title}</th>' for title in data["title"]
        )
        titles_size = len(titles_pdf)
        rows_email = data["values"]
        values_email = ""
        # print(values_email)
        values_pdf = [
            [value for index, value in enumerate(row) if index not in index_ignore]
            for row in data["values"]
        ]

        values_size = len(values_pdf)

        background_colors_table = {
            "1": colors.Color(1.0, 0.957, 0.800),
            "2": colors.whitesmoke,
        }

        background_colors_email = {
            "1": "background-color: rgb(255, 244, 204);",
            "2": "background-color: whitesmoke;",
        }

        if values_size == 0:
            colWidths = [usable_width / titles_size for i in range(titles_size)]
        else:
            length = usable_width / 100.0
            max_lengths = [(len(title) + cell) for title in titles_pdf]

            current_color = (background_colors_table["1"], background_colors_email["1"])
            current_departure = values_pdf[0][0]
            for i, (row_pdf, row_email) in enumerate(
                zip(values_pdf, rows_email), start=1
            ):
                departure = row_pdf[0]
                if departure != current_departure:
                    if current_color[0] == background_colors_table["2"]:
                        current_color = (
                            background_colors_table["1"],
                            background_colors_email["1"],
                        )
                    else:
                        current_color = (
                            background_colors_table["2"],
                            background_colors_email["2"],
                        )
                    current_departure = departure

                # print(row_pdf)
                values_email += (
                    f'<tr style="{current_color[1]}">'
                    + "".join(
                        f'<td style="text-align: center;">{value}</td>'
                        for value in row_email
                    )
                    + "</tr>"
                )

                # print(values_email)

                total_rolls += int(row_pdf[5])
                total_weight += float(row_pdf[6])
                # print("-> rolls", row[5])
                # print("-> width", row[6])
                style.add("BACKGROUND", (0, i), (-1, i), current_color[0])
                for j, value in enumerate(row_pdf):
                    max_lengths[j] = max(max_lengths[j], len(value) + cell)

            colWidths = [
                (current_length * (cell + current_length))
                for current_length in max_lengths
            ]

            colWidths_sum = sum(colWidths)
            max_lengths_sum = sum(max_lengths)
            colWidths_size = len(colWidths)
            if max_lengths_sum < 100:
                colWidths = [
                    width + (usable_width - colWidths_sum / colWidths_size)
                    for width in colWidths
                ]
            else:
                diff = max_lengths_sum - 100.0
                while diff > 0:
                    max_value = max(max_lengths)
                    for i in range(len(max_lengths)):
                        if max_lengths[i] == max_value:
                            max_lengths[i] -= 1
                            diff -= 1
                            if diff == 0:
                                break
                colWidths = [
                    (length * current_length) for current_length in max_lengths
                ]
        return (
            colWidths,
            titles_pdf,
            values_pdf,
            titles_email,
            values_email,
            style,
            total_rolls,
            total_weight,
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

    async def send_email_pdf(
        self,
        name_pdf: str,
        name_pdf_send: str,
        fecha: str,
        data: dict,
    ):
        body_email = PROGRAMACION_TINTORERIA_HTML.format(
            data["from"],
            fecha,
            data["title"],
            data["values"],
            data["rolls"],
            data["weights"],
        )

        with open(name_pdf, "rb") as pdf_file:
            pdf_data = pdf_file.read()

        encoded_pdf = base64.b64encode(pdf_data).decode("utf-8")

        subject_email = PROGRAMACION_TINTORERIA_ASUNTO.format(data["semana"])

        params: resend.Emails.SendParams = {
            "from": "practicante.sistemas@boston.com.pe",
            "to": data["email_to"],
            "subject": subject_email,
            "html": body_email,
            "attachments": [
                {
                    "filename": name_pdf_send,
                    "content": encoded_pdf,
                    "content_type": "application/pdf",
                }
            ],
        }

        email = resend.Emails.send(params)
        return email

    async def send_email_pdf_table(
        self,
        data: dict,
    ):
        fecha = datetime.now(timezone).strftime("%Y-%m-%d")

        orientation = 0
        pagesize = letter if orientation == 0 else landscape(letter)
        first_height = 420 if orientation == 0 else 250
        limit_first_height = 528 if orientation == 0 else 336
        last_height = 558 if orientation == 0 else 396
        limit_last_height = 648 if orientation == 0 else 486
        celda = 3.5 if orientation == 0 else 1.5

        page_width, page_height = pagesize
        left_margin = 0.85 * inch
        right_margin = 0.85 * inch
        usable_width = page_width - left_margin - right_margin

        style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Roboto-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTNAME", (0, 1), (-1, -1), "Roboto"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
            ]
        )

        data_length = {
            "usable_width": usable_width,
            "cell": celda,
            "pagesize": pagesize,
            "first_height": first_height,
            "limit_first_height": limit_first_height,
            "last_height": last_height,
            "limit_last_height": limit_last_height,
        }

        (
            colWidths,
            titles_pdf,
            values_pdf,
            titles_email,
            values_email,
            style,
            total_rolls,
            total_weight,
        ) = self.data_processing(data, data_length, style)
        name_pdf = str(uuid.uuid4()) + ".pdf"
        image_path = "src/core/assets/images/logo1.png"
        reduction_percentaje = 87
        orientation = False

        data_table_pdf = data
        data_table_pdf["title"] = titles_pdf
        data_table_pdf["values"] = values_pdf
        self.pdf_service.generate_pdf(
            name_pdf,
            image_path,
            reduction_percentaje,
            data_table_pdf,
            data_length,
            orientation,
            fecha,
            colWidths,
            style,
        )

        data_table_email = data
        data_table_email["title"] = titles_email
        data_table_email["values"] = values_email
        data_table_email["rolls"] = total_rolls
        data_table_email["weights"] = total_weight

        await self.send_email_pdf(name_pdf, "reporte.pdf", fecha, data_table_email)

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
        await self.send_email(settings.EMAIL_FROM, [email_to], subject, html_content)

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

        await self.send_email(settings.EMAIL_FROM, [email_to], subject, html_content)

    async def send_reset_password_email(
        self, email_to: str, display_name: str, password: str
    ):
        subject = "Nueva Contraseña - SISTEMAS MECSA"
        template = self.template_env.get_template("send_reset_password_email.html")
        html_content = template.render(
            LOGO_MECSA=LOGO_MECSA,
            display_name=display_name,
            password=password,
            FRONTEND_URL=settings.FRONTEND_URL,
        )

        await self.send_email(settings.EMAIL_FROM, [email_to], subject, html_content)
