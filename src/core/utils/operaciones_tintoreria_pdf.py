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

orientation = 0
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


def draw_comments_section(canvas, doc, comments, cant_page):
    if doc.page == cant_page:
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
    canvas, doc, data, image_path, reduction_percentage, cant_page
):
    draw_background(canvas, doc)
    draw_image(canvas, doc, image_path, reduction_percentage)
    draw_signature(canvas, doc)
    draw_comments_section(canvas, doc, data["comments"], cant_page)


def on_later_pages_programacion(canvas, doc, data, cant_page):
    draw_background(canvas, doc)
    draw_signature(canvas, doc)
    draw_comments_section(canvas, doc, data["comments"], cant_page)


def generate_pdf_programacion(
    name_pdf: str,
    image_path: str,
    reduction_percentage: float,
    data: dict,
    lengths: dict,
    orientation: bool,
    fecha: str,
    colWidths: list,
    table_style: TableStyle,
):
    pagesize = lengths["pagesize"]
    first_height = lengths["first_height"]
    limit_first_height = lengths["limit_first_height"]
    last_height = lengths["last_height"]
    limit_last_height = lengths["limit_last_height"]

    pdf = SimpleDocTemplate(
        name_pdf,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        pagesize=pagesize,
    )

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

    elements.append(Paragraph("Fecha:", styles["Roboto"]))
    elements.append(Paragraph(fecha, styles["Roboto"]))
    elements.append(Spacer(1, 12))

    titulo = (
        "<font size=17><b>Programación Tintorería Semana:</b> <b>{0}</b></font>".format(
            data["semana"]
        )
    )

    elements.append(Paragraph(titulo, styles["Roboto-Bold"]))
    elements.append(Spacer(1, 24))

    valor = [
        ["Desde Tejeduría: ", data["from"]],
        ["", ""],
        ["A Tintorería: ", data["to"]],
    ]

    table = draw_table_header(valor, pagesize)

    elements.append(table)
    elements.append(Spacer(1, 24))

    titles = [Paragraph(title, styles["Roboto-Bold-Small"]) for title in data["title"]]
    values = [
        [Paragraph(i, styles["Roboto-Small"]) for i in row] for row in data["values"]
    ]

    data_table = [titles] + values

    table = Table(data_table, colWidths=colWidths)

    width, height = table.wrap(0, 0)

    table.setStyle(table_style)

    elements.append(table)

    cant_page = 1

    if first_height < height <= limit_first_height:
        cant_page += 1
        elements.append(PageBreak())
        elements.append(Spacer(1, 2))
    elif height > limit_first_height:
        height = height - limit_first_height
        cant_page += 1

        while height > limit_last_height:
            cant_page += 1
            height -= limit_last_height

        if last_height < height:
            cant_page += 1
            elements.append(PageBreak())
            elements.append(Spacer(1, 2))

    pdf.build(
        elements,
        onFirstPage=lambda canvas, doc: on_first_page_programacion(
            canvas, doc, data, image_path, reduction_percentage, cant_page
        ),
        onLaterPages=lambda canvas, doc: on_later_pages_programacion(
            canvas, doc, data, cant_page
        ),
    )
