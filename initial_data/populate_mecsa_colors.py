import asyncio

import httpx

# URL base de tu API (ajusta esto según tu configuración)
BASE_URL = "http://localhost:8000"
URI = BASE_URL + "/operations/v1/color-mecsa"

# Datos de ejemplo para poblar la tabla
colors_data = [
    {"name": "NEGRO", "sku": "NEGRO", "hexadecimal": "#000000"},
    {"name": "BLANCO", "sku": "BLAN", "hexadecimal": "#FFFFFF"},
    {"name": "ROJO", "sku": "ROJO", "hexadecimal": "#FF0000"},
    {"name": "VERDE", "sku": "VERDE", "hexadecimal": "#00FF00"},
    {"name": "AZUL", "sku": "AZUL", "hexadecimal": "#0000FF"},
    {"name": "AMARILLO", "sku": "AMAR", "hexadecimal": "#FFFF00"},
    {"name": "CIAN", "sku": "CIAN", "hexadecimal": "#00FFFF"},
    {"name": "MAGENTA", "sku": "MAG", "hexadecimal": "#FF00FF"},
    {"name": "GRIS", "sku": "GRIS", "hexadecimal": "#808080"},
    {"name": "NARANJA", "sku": "NARAN", "hexadecimal": "#FFA500"},
    {"name": "ROSA", "sku": "ROSA", "hexadecimal": "#FFC0CB"},
    {"name": "MARRON", "sku": "MARR", "hexadecimal": "#A52A2A"},
    {"name": "PURPURA", "sku": "PURPU", "hexadecimal": "#800080"},
    {"name": "VIOLETA", "sku": "VIOL", "hexadecimal": "#EE82EE"},
    {"name": "TURQUESA", "sku": "TURQ", "hexadecimal": "#40E0D0"},
    {"name": "DORADO", "sku": "DOR", "hexadecimal": "#FFD700"},
    {"name": "PLATEADO", "sku": "PLATA", "hexadecimal": "#C0C0C0"},
    {"name": "BEIGE", "sku": "BEIGE", "hexadecimal": "#F5F5DC"},
    {"name": "LAVANDA", "sku": "LAVAN", "hexadecimal": "#E6E6FA"},
    {"name": "DURAZNO", "sku": "DUR", "hexadecimal": "#FFDAB9"},
    {"name": "CHOCOLATE", "sku": "CHOCO", "hexadecimal": "#D2691E"},
]


async def populate_mecsa_colors():
    async with httpx.AsyncClient() as client:
        for color in colors_data:
            response = await client.post(f"{URI}/", json=color, timeout=120)
            if response.status_code == 201:
                print(f"Color '{color['name']}' creado con éxito.")
            else:
                print(f"Error al crear el color '{color['name']}': {response.json()}")


asyncio.run(populate_mecsa_colors())
