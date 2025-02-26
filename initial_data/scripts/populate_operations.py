import asyncio

from config import populate

from src.core.database import get_db
from src.security.models import Operation


async def populate_operations() -> None:
    filename = "operation.json"
    async for db in get_db():
        await populate(db=db, model=Operation, filename=filename)


if __name__ == "__main__":
    asyncio.run(populate_operations())
