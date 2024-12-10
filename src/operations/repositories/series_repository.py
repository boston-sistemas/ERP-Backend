from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import Series


class SeriesRepository(BaseRepository[Series]):
    def __init__(self, db: AsyncSession, flush: bool = False):
        super().__init__(Series, db, flush)

    async def find_series_by_id(
        self, document_code: str, service_number: int
    ) -> Series | None:
        id = {
            "company_code": MECSA_COMPANY_CODE,
            "document_code": document_code,
            "service_number": service_number,
        }
        return await self.find_by_id(id=id)
