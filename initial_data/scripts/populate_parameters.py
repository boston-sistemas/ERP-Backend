import asyncio

from config import populate

from src.core.database import get_db
from src.security.models import Parameter


async def populate_parameters():
    filename = "parameters.json"
    async for db in get_db():
        await populate(db=db, model=Parameter, filename=filename)


if __name__ == "__main__":
    asyncio.run(populate_parameters())
