from sqlalchemy import Sequence

from src.core.database import PromecBase

product_id_seq = Sequence(
    name="product_id_seq",
    start=100100100100,
    metadata=PromecBase.metadata,
)

color_id_seq = Sequence("color_id_seq", start=100100, metadata=PromecBase.metadata)
