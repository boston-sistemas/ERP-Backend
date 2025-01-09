from src.operations.schemas import (
    CardOperationListSchema,
)

import os
import io

from pylatex import (
    Document,
    Command,
    NoEscape
)

import uuid
from src.operations.utils.card_operation.bar_code import generate_barcode

def read_and_delete_files(
    filenames: list[str],
    card_pdf_filename_path: str,
):
    path = os.path.dirname(card_pdf_filename_path)
    card_pdf_filename_path = f"{card_pdf_filename_path}.pdf"
    with open(card_pdf_filename_path, "rb") as f:
        pdf = io.BytesIO(f.read())

    for filename in filenames:
        # print(f"{path}/{filename}")
        os.remove(f"{path}/{filename}")

    os.remove(card_pdf_filename_path)

    return pdf

def generate_pdf_cards(
    cards: CardOperationListSchema,
):
    doc = Document(documentclass="article")
    doc.preamble.append(Command('input', 'card.tex'))

    doc.append(Command('thispagestyle', 'empty'))

    card_pdf_filename = str(uuid.uuid4())
    card_pdf_filename_path = f"src/operations/utils/card_operation/{card_pdf_filename}"
    card_images_filenames = []

    for card in cards.card_operations:
        filename = generate_barcode(card.id)
        image = f"{filename}.png"
        id = card.id
        product_id = card.product_id
        net_weight = card.net_weight
        tint_supplier_id = card._supplier_tint_initials
        weaving_supplier_id = card._supplier_weaving_tej_initials
        yarn_supplier_id = ""
        for supplier_yarn in card._supplier_yarn_initials:
            yarn_supplier_id += supplier_yarn + ", "

        yarn_supplier_id = yarn_supplier_id[:-2]

        service_order = ""
        for service_order_id in card.service_orders:
            service_order += service_order_id + ", "

        service_order = service_order[:-2]

        card_type = "N"
        print(filename)
        command = f"""
        \\GenerateBarcodeCard{{{image}}}{{{id}}}{{{product_id}}}{{{net_weight}}}{{{service_order}}}{{{tint_supplier_id}}}{{{weaving_supplier_id}}}{{{yarn_supplier_id}}}{{{card_type}}}
        """
        doc.append(NoEscape(command))
        doc.append(Command('newpage'))
        card_images_filenames.append(image)

    doc.generate_pdf(card_pdf_filename_path, clean_tex=True)

    pdf = read_and_delete_files(
        card_images_filenames,
        card_pdf_filename_path,
    )

    return pdf
