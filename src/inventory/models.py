from datetime import datetime

from sqlalchemy import (
    PrimaryKeyConstraint,
    String,
)

from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import PromecBase

from src.inventory.constants import (
    MAX_LENGTH_CODCIA,
    MAX_LENGTH_TPOOC,
    MAX_LENGTH_NROOC,
    MAX_LENGTH_CODPRO,
    MAX_LENGTH_FLGEST,
    MAX_LENGTH_CODPROD,
    MAX_LENGTH_CODUND,
)

class OrdenCompra(PromecBase):
    __tablename__ = "opecocmp"
    __table_args__ = {"schema": "PUB"}

    codcia: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CODCIA))
    tpooc: Mapped[str] = mapped_column(String(length=MAX_LENGTH_TPOOC))
    nrooc: Mapped[str] = mapped_column(String(length=MAX_LENGTH_NROOC))
    codpro: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CODPRO))
    fchemi: Mapped[datetime] = mapped_column()
    fchvto: Mapped[datetime] = mapped_column()
    codmon: Mapped[int] = mapped_column()
    flgest: Mapped[str] = mapped_column(String(length=MAX_LENGTH_FLGEST))

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "tpooc", "nrooc"),
    )

class OrdenCompraDetalle(PromecBase):
    __tablename__ = "opedocmp"
    __table_args__ = {"schema": "PUB"}

    codcia: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CODCIA))
    tpooc: Mapped[str] = mapped_column(String(length=MAX_LENGTH_TPOOC))
    nrooc: Mapped[str] = mapped_column(String(length=MAX_LENGTH_NROOC))
    codprod: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CODPROD))
    canord: Mapped[float] = mapped_column()
    canate: Mapped[float] = mapped_column()
    flgest: Mapped[str] = mapped_column(String(length=MAX_LENGTH_FLGEST))
    codund: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CODUND))

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "tpooc", "nrooc", "codprod"),
    )
