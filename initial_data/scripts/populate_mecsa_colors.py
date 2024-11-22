import asyncio

from config import populate

from src.core.database import get_promec_db
from src.operations.models import MecsaColor


async def populate_mecsa_colors():
    filename = "mecsa_colors.json"
    async for promec_db in get_promec_db():
        await populate(db=promec_db, model=MecsaColor, filename=filename)


if __name__ == "__main__":
    asyncio.run(populate_mecsa_colors())
