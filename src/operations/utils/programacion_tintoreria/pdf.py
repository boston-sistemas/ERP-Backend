import base64
import os
import uuid

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.models import Proveedor

from .constants import (
    PDFTintoreriaHorizontal,
    PDFTintoreriaVertical,
)

pdfmetrics.registerFont(
    TTFont("Roboto", "src/core/assets/fonts/Roboto/Roboto-Regular.ttf")
)
pdfmetrics.registerFont(
    TTFont("Roboto-Bold", "src/core/assets/fonts/Roboto/Roboto-Bold.ttf")
)


def draw_image(canvas, doc, image_path, reduction_percentage):
    image = PILImage.open(image_path)
    original_width, original_height = image.size

    width = original_width * (1 - reduction_percentage / 100)
    height = original_height * (1 - reduction_percentage / 100)

    width = width / image.info["dpi"][0] * inch
    height = height / image.info["dpi"][1] * inch

    x_position = doc.pagesize[0] - doc.rightMargin * 1.1 - width
    y_position = doc.pagesize[1] - doc.topMargin * 1.1 - height

    canvas.drawImage(
        image_path,
        x_position,
        y_position,
        width=width,
        height=height,
        preserveAspectRatio=True,
    )


def draw_background(canvas, doc):
    canvas.saveState()
    width, height = doc.pagesize
    margin = 0.5 * inch
    canvas.setFillColorRGB(1, 1, 1)
    canvas.rect(margin, margin, width - 2 * margin, height - 2 * margin, fill=1)
    canvas.restoreState()


def draw_comments_section(canvas, doc, comments, partidas_size, comment_page) -> None:
    if doc.page != comment_page:
        return None

    if comments is None:
        comments = f"Programación de {partidas_size} {'partidas' if partidas_size > 1 else 'partida'}."
    canvas.saveState()
    width, height = doc.pagesize
    margin = 0.5 * inch

    rect_x = margin
    rect_y = margin
    rect_width = width - 2 * margin
    rect_height = 1.5 * inch

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Roboto", fontName="Roboto", fontSize=10))
    comment_paragraph = Paragraph(comments, styles["Roboto"])

    avail_width = rect_width - 0.8 * inch
    avail_height = rect_height - 0.2 * inch
    w, h = comment_paragraph.wrap(avail_width, avail_height)

    rect_height = max(rect_height, h + inch)

    canvas.setFillColorRGB(0.95, 0.95, 0.95)
    canvas.rect(rect_x, rect_y, rect_width, rect_height, stroke=1, fill=1)

    canvas.setFillColorRGB(0, 0, 0)
    canvas.setFont("Roboto-Bold", 12)
    canvas.drawString(
        rect_x + 0.35 * inch, rect_y + rect_height - 0.4 * inch, "Comentarios:"
    )

    comment_paragraph.drawOn(
        canvas, rect_x + 0.35 * inch, rect_y + rect_height - 0.6 * inch - h
    )

    canvas.restoreState()


def draw_signature(canvas, doc):
    canvas.saveState()
    width, height = doc.pagesize
    margin = 0.5 * inch

    canvas.setFillColorRGB(0, 0, 0.5)
    canvas.setFont("Roboto-Bold", 12)
    canvas.drawString(width - margin - 1.11 * inch, margin / 2, "OPERACIONES")
    canvas.restoreState()


def draw_table_header(values: list, pagesize: tuple):
    # print(values)
    page_width, page_height = pagesize
    left_margin = 0.85 * inch
    right_margin = 0.85 * inch
    usable_width = page_width - left_margin - right_margin
    table = Table(
        values, colWidths=[usable_width * (1 / 3.0), usable_width * (2 / 3.0)]
    )

    table.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (0, 2), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("BACKGROUND", (0, 0), (0, 1), colors.white),
                ("TEXTCOLOR", (0, 0), (0, 1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, -1), "Roboto"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("GRID", (1, 0), (1, 0), 1, colors.black),
                ("GRID", (1, 2), (1, 2), 1, colors.black),
            ]
        )
    )

    return table


def on_first_page_programacion(
    canvas, doc, comment, partidas_size, image_path, reduction_percentage, comment_page
):
    draw_background(canvas, doc)
    draw_image(canvas, doc, image_path, reduction_percentage)
    draw_signature(canvas, doc)
    draw_comments_section(canvas, doc, comment, partidas_size, comment_page)


def on_later_pages_programacion(canvas, doc, comment, partidas_size, comment_page):
    draw_background(canvas, doc)
    draw_signature(canvas, doc)
    draw_comments_section(canvas, doc, comment, partidas_size, comment_page)


def add_dyeing_schedule_to_elements(
    elements: list, tejeduria: Proveedor, tintoreria: Proveedor, pagesize: tuple, styles
):
    fecha = calculate_time(timezone=PERU_TIMEZONE).strftime("%d/%m/%Y")
    semana = calculate_time(timezone=PERU_TIMEZONE).isocalendar()[1]

    elements.append(Paragraph("Fecha:", styles["Roboto"]))
    elements.append(Paragraph(fecha, styles["Roboto"]))
    elements.append(Spacer(1, 12))

    titulo = (
        "<font size=17><b>Programación Tintorería Semana:</b> <b>{0}</b></font>".format(
            semana
        )
    )

    elements.append(Paragraph(titulo, styles["Roboto-Bold"]))
    elements.append(Spacer(1, 24))

    valor = [
        ["Desde Tejeduría: ", tejeduria.razon_social],
        ["", ""],
        ["A Tintorería: ", tintoreria.razon_social],
    ]

    table = draw_table_header(valor, pagesize)
    elements.append(table)
    elements.append(Spacer(1, 24))


def set_table_style(
    lengths: PDFTintoreriaHorizontal | PDFTintoreriaVertical,
    titles_pdf: list,
    values_pdf: list,
    styles_pdf: dict,
) -> None:
    titles = [Paragraph(title, styles_pdf["Roboto-Bold-Small"]) for title in titles_pdf]

    if len(values_pdf) == 0:
        return [titles]

    background_colors_table = lengths.background_colors_table
    style = lengths.style
    index_color = 0
    current_color = background_colors_table[index_color]
    current_departure = values_pdf[0][0]
    for i, row_pdf in enumerate(values_pdf, start=1):
        departure = row_pdf[0]
        if departure != current_departure:
            index_color += 1
            current_color = background_colors_table[(index_color % 2)]
            current_departure = departure

        style.add("BACKGROUND", (0, i), (-1, i), current_color)

    values = [
        [Paragraph(i, styles_pdf["Roboto-Small"]) for i in row] for row in values_pdf
    ]

    return [titles] + values


def set_max_lengths(
    lengths: PDFTintoreriaHorizontal | PDFTintoreriaVertical,
    values_pdf: list,
    titles_pdf: list,
):
    colWidths = []
    usable_width = lengths.usable_width
    cell = lengths.celda
    values_size = len(values_pdf)

    if values_size == 0:
        colWidths = [usable_width / len(titles_pdf) for i in range(len(titles_pdf))]
        return colWidths

    length = usable_width / 100.0
    max_lengths = [(len(title) + cell) for title in titles_pdf]
    for row_pdf in values_pdf:
        for j, value in enumerate(row_pdf):
            max_lengths[j] = max(max_lengths[j], len(value) + cell)

    colWidths = [(length * (current_length)) for current_length in max_lengths]
    max_lengths_sum = sum(max_lengths)
    colWidths_size = len(colWidths)
    if max_lengths_sum < 100:
        colWidths = [
            width + ((usable_width / colWidths_size) - width) for width in colWidths
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
        colWidths = [(length * current_length) for current_length in max_lengths]

    return colWidths


def add_table_to_elements(
    elements: list,
    data: list,
    lengths: PDFTintoreriaHorizontal | PDFTintoreriaVertical,
    styles_pdf,
):
    colWidths = []
    titles_pdf = data[0][:]
    values_pdf = data[1:][:]

    colWidths = set_max_lengths(lengths, values_pdf, titles_pdf)
    data_table = set_table_style(lengths, titles_pdf, values_pdf, styles_pdf)

    table = Table(data_table, colWidths=colWidths)
    table.setStyle(lengths.style)
    elements.append(table)

    return table


def calculate_comment_page(
    lengths: PDFTintoreriaHorizontal | PDFTintoreriaVertical,
    elements: list,
    height: float,
):
    first_height = lengths.first_height
    limit_first_height = lengths.limit_first_height
    last_height = lengths.last_height
    limit_last_height = lengths.limit_last_height

    comment_page = 1

    if first_height < height <= limit_first_height:
        comment_page += 1
        elements.append(PageBreak())
        elements.append(Spacer(1, 2))
    elif height > limit_first_height:
        height = height - limit_first_height
        comment_page += 1

        while height > limit_last_height:
            comment_page += 1
            height -= limit_last_height

        if last_height < height:
            comment_page += 1
            elements.append(PageBreak())
            elements.append(Spacer(1, 2))


def generate_pdf(
    tejeduria: Proveedor,
    tintoreria: Proveedor,
    comment: str,
    partidas_size: int,
    table: list,
):
    attributes = PDFTintoreriaVertical()

    pagesize = attributes.pagesize

    reduction_percentage = 87
    image_path = "src/core/assets/images/logo1.png"

    pdf_name = str(uuid.uuid4()) + ".pdf"
    elements = []
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name="Roboto", fontName="Roboto", fontSize=10))
    styles.add(ParagraphStyle(name="Roboto-Bold", fontName="Roboto-Bold", fontSize=17))

    styles.add(
        ParagraphStyle(
            name="Roboto-Bold-Small",
            fontName="Roboto-Bold",
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Roboto-Small",
            fontName="Roboto",
            fontSize=8,
            textColor=colors.black,
            alignment=TA_CENTER,
        )
    )

    pdf = SimpleDocTemplate(
        pdf_name,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        pagesize=pagesize,
    )

    add_dyeing_schedule_to_elements(elements, tejeduria, tintoreria, pagesize, styles)
    table = add_table_to_elements(elements, table, attributes, styles)

    width, height = table.wrap(0, 0)
    comment_page = calculate_comment_page(attributes, elements, height)
    pdf.build(
        elements,
        onFirstPage=lambda canvas, doc: on_first_page_programacion(
            canvas,
            doc,
            comment,
            partidas_size,
            image_path,
            reduction_percentage,
            comment_page,
        ),
        onLaterPages=lambda canvas, doc: on_later_pages_programacion(
            canvas, doc, comment, partidas_size, comment_page
        ),
    )

    with open(pdf_name, "rb") as file:
        pdf_file = file.read()

    encoded_pdf = base64.b64encode(pdf_file).decode("utf-8")
    os.remove(pdf_name)

    return encoded_pdf
