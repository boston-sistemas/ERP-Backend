from sqlalchemy.orm import Mapped, mapped_column

from src.operations.models import (
    OrdenCompra,
    OrdenCompraDetalle,
)


class TestOrdenCompra(OrdenCompra):
    nota: Mapped[str] = mapped_column()
    atencion: Mapped[str] = mapped_column()
    impvta: Mapped[float] = mapped_column()
    impigv: Mapped[float] = mapped_column()
    imptot: Mapped[float] = mapped_column()
    impbto: Mapped[float] = mapped_column()
    impdto: Mapped[float] = mapped_column()
    idusers: Mapped[str] = mapped_column()
    flgatc: Mapped[str] = mapped_column()
    lugent: Mapped[str] = mapped_column()
    plazoent: Mapped[str] = mapped_column()
    flgprt: Mapped[str] = mapped_column()
    nroser: Mapped[str] = mapped_column()


class TestOrdenCompraDetalle(OrdenCompraDetalle):
    pordto: Mapped[str] = mapped_column()
    aftigv: Mapped[bool] = mapped_column()
    factor: Mapped[float] = mapped_column()
    detalle: Mapped[str] = mapped_column()
