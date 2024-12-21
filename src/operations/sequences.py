from sqlalchemy import Sequence

from src.core.database import PromecBase

product_id_seq = Sequence(
    name="product_id_seq",
    start=100100100200,
    metadata=PromecBase.metadata,
)

color_id_seq = Sequence("color_id_seq", start=100150, metadata=PromecBase.metadata)

mecsa_batch_sq = Sequence("mecsa_batch_sq", start=1001001, metadata=PromecBase.metadata)
