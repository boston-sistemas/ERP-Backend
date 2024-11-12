from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession


class SequenceRepository:
    def __init__(self, sequence: Sequence, db: AsyncSession):
        self.sequence = sequence
        self.db = db

    async def next_value(self) -> int:
        value: int = (await self.db.execute(self.sequence.next_value())).scalar()
        return value
