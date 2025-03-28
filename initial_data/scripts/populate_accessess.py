import asyncio

from config import populate

from src.core.database import get_db
from src.security.models import Acceso, AccessOperation


async def populate_accesses():
    filename = "accesses.json"
    async for db in get_db():
        await populate(db=db, model=Acceso, filename=filename)

    filename = "access_operation.json"
    async for db in get_db():
        await populate(db=db, model=AccessOperation, filename=filename)


if __name__ == "__main__":
    asyncio.run(populate_accesses())
