import asyncio

from config import populate

from scripts.models_promec_test import (
    TestOrdenCompra,
    TestOrdenCompraDetalle,
)
from src.core.database import get_promec_db


async def populate_purchase_order():
    filename = "purchase_order.json"
    async for db in get_promec_db():
        await populate(db=db, model=TestOrdenCompra, filename=filename)

    filename = "purchase_order_detail.json"
    async for db in get_promec_db():
        await populate(db=db, model=TestOrdenCompraDetalle, filename=filename)


if __name__ == "__main__":
    asyncio.run(populate_purchase_order())
