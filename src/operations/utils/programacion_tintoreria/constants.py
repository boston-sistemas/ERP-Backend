from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.platypus import TableStyle

BACKGROUND_COLOR_EMAIL = {
    0: "background-color: rgb(255, 244, 204);",
    1: "background-color: whitesmoke;",
}


class PDFTintoreria:
    def __init__(self):
        self.left_margin = 0.85 * inch
        self.right_margin = 0.85 * inch
        self.style = TableStyle(
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
        self.background_colors_table = {
            0: colors.Color(1.0, 0.957, 0.800),
            1: colors.whitesmoke,
        }


class PDFTintoreriaVertical(PDFTintoreria):
    def __init__(self):
        super().__init__()
        self.orientation = 0
        self.pagesize = letter
        self.page_width, self.page_height = self.pagesize
        self.first_height = 420
        self.limit_first_height = 528
        self.last_height = 558
        self.limit_last_height = 648
        self.celda = 3.5
        self.usable_width = self.page_width - self.left_margin - self.right_margin


class PDFTintoreriaHorizontal(PDFTintoreria):
    def __init__(self):
        super().__init__()
        self.orientation = 1
        self.pagesize = landscape(letter)
        self.page_width, self.page_height = self.pagesize
        self.first_height = 250
        self.limit_first_height = 336
        self.last_height = 396
        self.limit_last_height = 486
        self.celda = 1.5
        self.usable_width = self.page_width - self.left_margin - self.right_margin
