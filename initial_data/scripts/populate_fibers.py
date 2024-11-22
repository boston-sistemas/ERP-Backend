import asyncio

from config import populate

from src.core.database import get_db
from src.operations.models import Fiber


async def populate_fibers():
    filename = "fibers.json"
    async for db in get_db():
        await populate(db=db, model=Fiber, filename=filename)


if __name__ == "__main__":
    asyncio.run(populate_fibers())
