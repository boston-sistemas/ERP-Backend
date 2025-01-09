import uuid

import barcode
from barcode.writer import ImageWriter


def generate_barcode(data: str, path: str = "src/operations/utils/card_operation/"):
    Code128 = barcode.get_barcode_class("code128")
    my_code = Code128(data, writer=ImageWriter())
    filename = str(uuid.uuid4())
    filename_path = f"{path}{filename}"
    my_code.save(
        filename_path,
        options={
            "write_text": False,
            "font_size": 0,
            "module_width": 0.18,
            "module_height": 10,
            "dpi": 300,
            "quiet_zone": 0.5,
            "text_distance": 0,
        },
    )

    return filename
