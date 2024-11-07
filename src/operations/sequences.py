from sqlalchemy import Sequence

from src.core.database import Base

product_id_seq = Sequence(
    "product_id_seq", start=100100100100, maxvalue=999999999999, metadata=Base.metadata
)

color_id_seq = Sequence(
    "color_id_seq", start=100100, maxvalue=999999, metadata=Base.metadata
)
