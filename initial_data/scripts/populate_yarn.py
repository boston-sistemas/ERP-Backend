import asyncio

from config import populate

from src.core.database import get_db, get_promec_db
from src.operations.models import InventoryItem, YarnFiber


async def populate_yarns():
    filename = "yarns.json"
    async for db in get_promec_db():
        await populate(db=db, model=InventoryItem, filename=filename)

    filename = "yarn_recipes.json"
    async for db in get_db():
        await populate(db=db, model=YarnFiber, filename=filename)


if __name__ == "__main__":
    asyncio.run(populate_yarns())
