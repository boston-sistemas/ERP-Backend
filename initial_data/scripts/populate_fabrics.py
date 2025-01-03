import asyncio

from config import populate
from populate_barcode import set_barcode

from src.core.database import get_promec_db
from src.operations.models import FabricYarn, InventoryItem


async def populate_fabrics():
    filename = "fabrics.json"
    async for db in get_promec_db():
        await populate(db=db, model=InventoryItem, filename=filename)
        await set_barcode(filename=filename)

    filename = "fabric_recipes.json"
    async for db in get_promec_db():
        await populate(db=db, model=FabricYarn, filename=filename)


if __name__ == "__main__":
    asyncio.run(populate_fabrics())
