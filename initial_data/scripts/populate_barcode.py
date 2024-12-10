from config import load_data, settings
from loguru import logger
from sqlalchemy.orm import load_only

from src.core.database import get_promec_db
from src.operations.models import InventoryItem
from src.operations.repositories import InventoryItemRepository
from src.operations.services import BarcodeSeries


async def set_barcode(filename: str):
    if not filename:
        return None

    items = load_data(settings.DATA_DIR + filename)
    ids = [item["id"] for item in items]

    async for db in get_promec_db():
        repository = InventoryItemRepository(db=db)
        barcode_series = BarcodeSeries(promec_db=db)
        filter = (InventoryItem.id.in_(ids)) & (InventoryItem.barcode == 0)
        inventory_items = await repository.find_items(
            filter=filter, options=(load_only(InventoryItem.id, InventoryItem.barcode),)
        )
        for inventory_item in inventory_items:
            inventory_item.barcode = await barcode_series.next_number()
            # logger.info(f"Codigo de barras asignado: {inventory_item.barcode}")

        await repository.save_all(inventory_items)
        logger.info(f"Codigo de Barras asignado: {str(ids)}")
