from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class ServiceOrderPCP(Base):
    __tablename__ = "tblordentejeduria"

    id: Mapped[str] = mapped_column("strordentejeduriaid", primary_key=True)
    supplier_id: Mapped[str] = mapped_column("strcodproveedortejeduriaid")
    period: Mapped[str] = mapped_column("strannoid")
    issue_date: Mapped[str] = mapped_column("dtmfechaemision")
    user_id: Mapped[float] = mapped_column("intusuarioregistroid")
    status: Mapped[str] = mapped_column("strdesestado")

    detail: Mapped[list["ServiceOrderPCPDetail"]] = relationship(
        "ServiceOrderPCPDetail",
        lazy="noload",
        primaryjoin="ServiceOrderPCP.id == ServiceOrderPCPDetail.order_id",
        foreign_keys="ServiceOrderPCPDetail.order_id",
    )

    __table_args__ = ({"schema": "public"},)


class ServiceOrderPCPDetail(Base):
    __tablename__ = "tblordentejeduriadetalle"

    order_id: Mapped[str] = mapped_column("strordentejeduriaid", primary_key=True)
    product_id: Mapped[str] = mapped_column("strcodproductoordtej", primary_key=True)
    quantity_ordered: Mapped[float] = mapped_column("intcantidad")
