from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.models import Proveedor

from .constants import BACKGROUND_COLOR_EMAIL


def calculate_total_rolls_and_weight(
    titles_table_email: list,
    values_table_email: list,
):
    index_rolls = titles_table_email.index("Rollos")
    index_weight = titles_table_email.index("Peso")

    total_rolls = 0
    total_weight = 0
    for row in values_table_email:
        total_rolls += int(row[index_rolls])
        total_weight += float(row[index_weight])
    return total_rolls, total_weight


def set_table_style(
    titles_table_email: list,
    values_table_email: list,
):
    background_color = BACKGROUND_COLOR_EMAIL

    rows_table = ""

    values_size = len(values_table_email)

    titles_table_email = "".join(
        f'<th style="text-align: center;">{title}</th>' for title in titles_table_email
    )

    if values_size == 0:
        return titles_table_email, ""

    current_departure = values_table_email[0][0]
    index_color = 0
    current_color = background_color[index_color]
    for row_email in values_table_email:
        departure = row_email[0]
        if departure != current_departure:
            index_color += 1
            current_departure = departure
            current_color = background_color[(index_color % 2)]

        rows_table += (
            f'<tr style="{current_color}">'
            + "".join(
                f'<td style="text-align: center;">{value}</td>' for value in row_email
            )
            + "</tr>"
        )

    return titles_table_email, rows_table


def generate_html(
    tejeduria: Proveedor,
    tintoreria: Proveedor,
    data: list,
    template_env: str,
):
    titles_email = data[0][:]

    values_email = data[1:][:]

    total_rolls, total_weight = calculate_total_rolls_and_weight(
        titles_email,
        values_email,
    )

    titles_table_email, values_table_email = set_table_style(
        titles_email,
        values_email,
    )

    fecha = calculate_time(tz=PERU_TIMEZONE).strftime("%d/%m/%Y")

    html_content = template_env.render(
        from_=tejeduria.razon_social,
        to=tintoreria.razon_social,
        date=fecha,
        titles=titles_table_email,
        values=values_table_email,
        rolls=total_rolls,
        weights=total_weight,
    )

    return html_content
