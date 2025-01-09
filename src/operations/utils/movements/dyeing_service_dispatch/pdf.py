import io

def generate_pdf():
    path = "src/operations/utils/movements/dyeing_service_dispatch/prueba.pdf"

    with open(path, "rb") as f:
        pdf = io.BytesIO(f.read())

    return pdf
