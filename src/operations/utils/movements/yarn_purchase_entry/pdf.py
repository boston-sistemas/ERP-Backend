
import io

def generate_pdf():
    path = "src/operations/utils/movements/yarn_purchase_entry/prueba.pdf"

    with open(path, "rb") as f:
        pdf = io.BytesIO(f.read())

    return pdf
