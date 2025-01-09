from datetime import date
from uuid import UUID

from sqlalchemy import (
    TIMESTAMP,
    ForeignKeyConstraint,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    and_,
    func,
    literal_column,
)
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from src.core.constants import ACTIVE_STATUS_PROMEC, MECSA_COMPANY_CODE
from src.core.database import Base, PromecBase
from src.operations.constants import (
    ANNULMENT_USER_ID_MAX_LENGTH,
    AUXILIARY_CODE_MAX_LENGTH,
    AUXILIARY_NAME_MAX_LENGTH,
    CARD_ID_MAX_LENGTH,
    CARD_TYPE_MAX_LENGTH,
    CLFAUX_MAX_LENGTH,
    CODCOL_MAX_LENGTH,
    COLOR_ID_MAX_LENGTH,
    COMPANY_CODE_MAX_LENGTH,
    DESTTEJ_MAX_LENGTH,
    DETDOC_MAX_LENGTH,
    DOCUMENT_CODE_MAX_LENGTH,
    DOCUMENT_NOTE_MAX_LENGTH,
    DOCUMENT_NUMBER_MAX_LENGTH,
    DRIVER_CODE_MAX_LENGTH,
    DRIVER_LICENSE_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    EMPQNRO2_MAX_LENGTH,
    EXIT_NUMBER_MAX_LENGTH,
    FABRIC_ID_MAX_LENGTH,
    FABRIC_TYPE_MAX_LENGTH,
    FIBER_DENOMINATION_MAX_LENGTH,
    FIBER_ID_MAX_LENGTH,
    FIBER_ORIGIN_MAX_LENGTH,
    FLGACT_MAX_LENGTH,
    FLGCBD_MAX_LENGTH,
    FLGELE_MAX_LENGTH,
    FLGRECLAMO_MAX_LENGTH,
    FLGSIT_MAX_LENGTH,
    GROUP_NUMBER_MAX_LENGTH,
    HASHCODE_MAX_LENGTH,
    INGRESS_NUMBER_MAX_LENGTH,
    INITIALS_MAX_LENGTH,
    INVENTORY_ITEM_PURCHASE_DESCRIPTION_MAX_LENGTH,
    MAX_LENGTH_COLOR_DESCRIPCION,
    MAX_LENGTH_COLOR_NOMBRE,
    MAX_LENGTH_CRUDO_ID,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ESTADO,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID,
    MAX_LENGTH_ORDEN_SERVICIO_TINTORERIA_CODIGO_MECSA,
    MAX_LENGTH_ORDEN_SERVICIO_TINTORERIA_ESTADO,
    MAX_LENGTH_PROVEEDOR_ALIAS,
    MAX_LENGTH_PROVEEDOR_ID,
    MAX_LENGTH_PROVEEDOR_RAZON_SOCIAL,
    MAX_LENGTH_SERVICIO_NOMBRE,
    MAX_LENGTH_TEJIDO_ID,
    MAX_LENGTH_TEJIDO_NOMBRE,
    MECSA_BATCH_MAX_LENGTH,
    MECSA_COLOR_ID_MAX_LENGTH,
    MOVEMENT_CODE_MAX_LENGTH,
    MOVEMENT_TYPE_MAX_LENGTH,
    NRODIR_MAX_LENGTH,
    NROGF_MAX_LENGTH,
    NROREQ_MAX_LENGTH,
    NROTARJ_MAX_LENGTH,
    ORIGIN_STATION_MAX_LENGTH,
    ORIGMOV_MAX_LENGTH,
    PAYMENT_METHOD_MAX_LENGTH,
    PREFELE_MAX_LENGTH,
    PRINTED_FLAG_MAX_LENGTH,
    PRODUCT_CODE_MAX_LENGTH,
    PURCHASE_ORDER_NUMBER_MAX_LENGTH,
    PURCHASE_ORDER_TYPE_MAX_LENGTH,
    REFERENCE_CODE_MAX_LENGTH,
    REFERENCE_DOCUMENT_MAX_LENGTH,
    REFERENCE_NUMBER_MAX_LENGTH,
    SERGF_MAX_LENGTH,
    SERIAL_NUMBER_MAX_LENGTH,
    SERVADI_MAX_LENGTH,
    SERVICE_CODE_MAX_LENGTH,
    SERVICE_ORDER_ID_MAX_LENGTH,
    SERVICE_ORDER_TYPE_MAX_LENGTH,
    STATUS_FLAG_MAX_LENGTH,
    STORAGE_CODE_MAX_LENGTH,
    SUPPLIER_ADDRESS_MAX_LENGTH,
    SUPPLIER_BATCH_MAX_LENGTH,
    SUPPLIER_CODE_MAX_LENGTH,
    SUPPLIER_COLOR_ID_MAX_LENGTH,
    SUPPLIER_NAME_MAX_LENGTH,
    SUPPLIER_RUC_MAX_LENGTH,
    TRANSACTION_MODE_MAX_LENGTH,
    TRANSACTION_MOTIVE_MAX_LENGTH,
    TRANSPORTER_CODE_MAX_LENGTH,
    UNDPESOBRUTOTOTAL_MAX_LENGTH,
    UNIT_CODE_MAX_LENGTH,
    USER_ID_MAX_LENGTH,
    VEHICLE_BRAND_MAX_LENGTH,
    VEHICLE_CODE_MAX_LENGTH,
    VEHICLE_PLATE_MAX_LENGTH,
    VOUCHER_NUMBER_MAX_LENGTH,
    YARN_ID_MAX_LENGTH,
    YARN_PURCHASE_ENTRY_DOCUMENT_CODE,
    YARN_PURCHASE_ENTRY_MOVEMENT_CODE,
    YARN_PURCHASE_ENTRY_MOVEMENT_TYPE,
    YARN_PURCHASE_ENTRY_STORAGE_CODE,
)
from src.security.models import Parameter


class Proveedor(Base):
    __tablename__ = "proveedor"

    proveedor_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_PROVEEDOR_ID))
    razon_social: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_PROVEEDOR_RAZON_SOCIAL),
        unique=True,
    )
    alias: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_PROVEEDOR_ALIAS),
        unique=True,
    )

    __table_args__ = (PrimaryKeyConstraint("proveedor_id"),)


class EspecialidadEmpresa(Base):
    __tablename__ = "especialidad_empresa"

    especialidad_id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_SERVICIO_NOMBRE),
        unique=True,
    )

    proveedores: Mapped[list[Proveedor]] = relationship(
        lazy="noload", secondary="proveedor_especialidad"
    )

    __table_args__ = (PrimaryKeyConstraint("especialidad_id"),)


class ProveedorEspecialidad(Base):
    __tablename__ = "proveedor_especialidad"

    proveedor_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_PROVEEDOR_ID))
    especialidad_id: Mapped[int] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("proveedor_id", "especialidad_id"),
        ForeignKeyConstraint(["proveedor_id"], ["proveedor.proveedor_id"]),
        ForeignKeyConstraint(
            ["especialidad_id"], ["especialidad_empresa.especialidad_id"]
        ),
    )


class Tejido(Base):
    __tablename__ = "tejido"

    tejido_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_TEJIDO_ID))
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_TEJIDO_NOMBRE),
    )

    __table_args__ = (PrimaryKeyConstraint("tejido_id"),)


class Crudo(Base):
    __tablename__ = "crudo"

    crudo_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CRUDO_ID))
    tejido_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_TEJIDO_ID),
    )
    densidad: Mapped[int] = mapped_column()
    ancho: Mapped[int] = mapped_column()
    galga: Mapped[int] = mapped_column()
    diametro: Mapped[int] = mapped_column()
    longitud_malla: Mapped[float] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("crudo_id"),
        ForeignKeyConstraint(["tejido_id"], ["tejido.tejido_id"]),
    )


class OrdenServicioTejeduria(Base):
    __tablename__ = "os_tejeduria"

    orden_servicio_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    tejeduria_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_PROVEEDOR_ID))
    fecha: Mapped[date] = mapped_column()
    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ESTADO)
    )

    proveedor: Mapped[Proveedor] = relationship(lazy="noload")
    detalles: Mapped[list["OrdenServicioTejeduriaDetalle"]] = relationship(
        lazy="noload"
    )

    __table_args__ = (
        PrimaryKeyConstraint("orden_servicio_tejeduria_id"),
        ForeignKeyConstraint(["tejeduria_id"], ["proveedor.proveedor_id"]),
    )


class OrdenServicioTejeduriaDetalle(Base):
    __tablename__ = "os_tejeduria_detalle"

    orden_servicio_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CRUDO_ID))
    programado_kg: Mapped[float] = mapped_column()
    consumido_kg: Mapped[float] = mapped_column()
    es_complemento: Mapped[bool] = mapped_column()
    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO)
    )
    reporte_tejeduria_nro_rollos: Mapped[int] = mapped_column()
    reporte_tejeduria_cantidad_kg: Mapped[float] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("orden_servicio_tejeduria_id", "crudo_id"),
        ForeignKeyConstraint(
            ["orden_servicio_tejeduria_id"],
            ["os_tejeduria.orden_servicio_tejeduria_id"],
        ),
        ForeignKeyConstraint(["crudo_id"], ["crudo.crudo_id"]),
    )


class OrdenServicioTejeduriaDetalleReporteLog(Base):
    __tablename__ = "orden_servicio_tejeduria_detalle_reporte_log"

    log_id: Mapped[UUID] = mapped_column()
    proveedor_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_PROVEEDOR_ID))
    orden_servicio_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CRUDO_ID))
    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO)
    )
    reporte_tejeduria_nro_rollos: Mapped[int] = mapped_column()
    reporte_tejeduria_cantidad_kg: Mapped[float] = mapped_column()
    created_at: Mapped[date] = mapped_column(TIMESTAMP, server_default=func.now())

    __table_args__ = (PrimaryKeyConstraint("log_id"),)


class Color(Base):
    __tablename__ = "color"

    color_id: Mapped[int] = mapped_column(Integer, Identity(start=1))
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_COLOR_NOMBRE), unique=True
    )
    descripcion: Mapped[str | None] = mapped_column(
        String(length=MAX_LENGTH_COLOR_DESCRIPCION), nullable=True
    )

    __table_args__ = (PrimaryKeyConstraint("color_id"),)

    def __repr__(self):
        return f"<Color(color_id='{self.color_id}',nombre='{self.nombre}')>"


class ProgramacionTintoreria(Base):
    __tablename__ = "programacion_tintoreria"

    id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    from_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_PROVEEDOR_ID)
    )
    to_tintoreria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_PROVEEDOR_ID)
    )

    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(["from_tejeduria_id"], ["proveedor.proveedor_id"]),
        ForeignKeyConstraint(["to_tintoreria_id"], ["proveedor.proveedor_id"]),
    )


class OrdenServicioTintoreria(Base):
    __tablename__ = "os_tintoreria"

    orden_servicio_tintoreria_id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    programacion_tintoreria_id: Mapped[int | None] = mapped_column()
    color_id: Mapped[int] = mapped_column()
    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TINTORERIA_ESTADO)
    )
    codigo_mecsa: Mapped[str | None] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TINTORERIA_CODIGO_MECSA), unique=True
    )

    __table_args__ = (
        PrimaryKeyConstraint("orden_servicio_tintoreria_id"),
        ForeignKeyConstraint(
            ["programacion_tintoreria_id"],
            ["programacion_tintoreria.id"],
        ),
        ForeignKeyConstraint(["color_id"], ["color.color_id"]),
    )


class OrdenServicioTintoreriaDetalle(Base):
    __tablename__ = "os_tintoreria_detalle"

    id: Mapped[int] = mapped_column(Identity(start=1))
    orden_servicio_tintoreria_id: Mapped[int] = mapped_column()
    orden_servicio_tejeduria_id: Mapped[str] = mapped_column(
        String(MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: Mapped[str] = mapped_column(String(MAX_LENGTH_CRUDO_ID))
    nro_rollos: Mapped[int] = mapped_column()
    cantidad_kg: Mapped[float] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["orden_servicio_tintoreria_id"],
            ["os_tintoreria.orden_servicio_tintoreria_id"],
        ),
        ForeignKeyConstraint(
            ["orden_servicio_tejeduria_id", "crudo_id"],
            [
                "os_tejeduria_detalle.orden_servicio_tejeduria_id",
                "os_tejeduria_detalle.crudo_id",
            ],
        ),
    )


class AbstractTableModel(PromecBase):
    __tablename__ = "admdtabla"

    table: Mapped[str] = mapped_column("tabla", primary_key=True)
    id: Mapped[str] = mapped_column("codigo", primary_key=True)
    is_active: Mapped[str] = mapped_column("Condicion", default=ACTIVE_STATUS_PROMEC)

    __table_args__ = ({"schema": "PUB"},)

    __mapper_args__ = {
        "polymorphic_abstract": True,
        "polymorphic_on": "table",
    }


class MecsaColor(AbstractTableModel):
    name: Mapped[str] = mapped_column("nombre")
    sku: Mapped[str] = mapped_column("VarChar1")
    hexadecimal: Mapped[str] = mapped_column("VarChar3")

    __mapper_args__ = {"polymorphic_identity": "COL"}


class SupplierColor(PromecBase):
    __tablename__ = "opecoltinto"

    supplier_id: Mapped[str] = mapped_column(
        "codpro", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    description: Mapped[str] = mapped_column(
        "descripcion", String(length=MAX_LENGTH_COLOR_DESCRIPCION)
    )
    id: Mapped[str] = mapped_column(
        "codigo", String(length=SUPPLIER_COLOR_ID_MAX_LENGTH)
    )

    __table_args__ = (
        PrimaryKeyConstraint("codpro", "codigo"),
        {"schema": "PUB"},
    )


class OrdenCompra(PromecBase):
    __tablename__ = "opecocmp"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    purchase_order_type: Mapped[str] = mapped_column(
        "tpooc", String(length=PURCHASE_ORDER_TYPE_MAX_LENGTH)
    )
    purchase_order_number: Mapped[str] = mapped_column(
        "nrooc", String(length=PURCHASE_ORDER_NUMBER_MAX_LENGTH)
    )
    supplier_code: Mapped[str] = mapped_column(
        "codpro", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    issue_date: Mapped[date] = mapped_column("fchemi")
    due_date: Mapped[date] = mapped_column("fchvto")
    currency_code: Mapped[int] = mapped_column("codmon")
    payment_method: Mapped[str] = mapped_column(
        "fmapgo", String(length=PAYMENT_METHOD_MAX_LENGTH)
    )
    status_flag: Mapped[str] = mapped_column(
        "flgest", String(length=STATUS_FLAG_MAX_LENGTH)
    )

    detail = relationship(
        "OrdenCompraDetalle",
        lazy="noload",
        primaryjoin=lambda: and_(
            OrdenCompra.company_code == OrdenCompraDetalle.company_code,
            OrdenCompra.purchase_order_type == OrdenCompraDetalle.purchase_order_type,
            OrdenCompra.purchase_order_number
            == OrdenCompraDetalle.purchase_order_number,
        ),
        back_populates="orden_compra",
        single_parent=True,  # one to many
        foreign_keys=lambda: [  # columnas usadas para la relación
            OrdenCompraDetalle.company_code,
            OrdenCompraDetalle.purchase_order_type,
            OrdenCompraDetalle.purchase_order_number,
        ],
    )

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "tpooc", "nrooc"),
        {"schema": "PUB"},
    )


class OrdenCompraDetalle(PromecBase):
    __tablename__ = "opedocmp"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    purchase_order_type: Mapped[str] = mapped_column(
        "tpooc", String(length=PURCHASE_ORDER_TYPE_MAX_LENGTH)
    )
    purchase_order_number: Mapped[str] = mapped_column(
        "nrooc", String(length=PURCHASE_ORDER_NUMBER_MAX_LENGTH)
    )
    product_code: Mapped[str] = mapped_column(
        "codprod", String(length=PRODUCT_CODE_MAX_LENGTH)
    )
    quantity_ordered: Mapped[float] = mapped_column("canord")
    quantity_supplied: Mapped[float] = mapped_column("canate")
    status_flag: Mapped[str] = mapped_column(
        "flgest", String(length=STATUS_FLAG_MAX_LENGTH)
    )
    unit_code: Mapped[str] = mapped_column(
        "codund", String(length=UNIT_CODE_MAX_LENGTH)
    )
    precto: Mapped[float] = mapped_column("precto")
    impcto: Mapped[float] = mapped_column("impcto")

    orden_compra = relationship(
        "OrdenCompra",
        lazy="noload",
        primaryjoin=lambda: and_(
            OrdenCompra.company_code == OrdenCompraDetalle.company_code,
            OrdenCompra.purchase_order_type == OrdenCompraDetalle.purchase_order_type,
            OrdenCompra.purchase_order_number
            == OrdenCompraDetalle.purchase_order_number,
        ),
        back_populates="detail",
        foreign_keys=lambda: [
            OrdenCompraDetalle.company_code,
            OrdenCompraDetalle.purchase_order_type,
            OrdenCompraDetalle.purchase_order_number,
        ],
    )

    yarn = relationship(
        "InventoryItem",
        lazy="noload",
        primaryjoin=lambda: and_(
            OrdenCompraDetalle.company_code == InventoryItem.company_code,
            OrdenCompraDetalle.product_code == InventoryItem.id,
        ),
        foreign_keys=lambda: [
            OrdenCompraDetalle.company_code,
            OrdenCompraDetalle.product_code,
        ],
        viewonly=True,
    )

    # elastico

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "tpooc", "nrooc", "codprod"),
        {"schema": "PUB"},
    )

    def __repr__(self):
        return f"<OrdenCompraDetalle(codprod={self.product_code}>"


class ServiceOrder(PromecBase):
    __tablename__ = "opecosmp"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    _type: Mapped[str] = mapped_column(
        "tpoos", String(length=SERVICE_ORDER_TYPE_MAX_LENGTH)
    )
    id: Mapped[str] = mapped_column("nroos", String(length=SERVICE_ORDER_ID_MAX_LENGTH))
    supplier_id: Mapped[str] = mapped_column(
        "codpro", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    issue_date: Mapped[date] = mapped_column("fchemi")
    due_date: Mapped[date] = mapped_column("fchvto")
    currency_code: Mapped[int] = mapped_column("codmon", default=1)
    payment_method: Mapped[str] = mapped_column(
        "fmapgo", String(length=PAYMENT_METHOD_MAX_LENGTH)
    )
    status_flag: Mapped[str] = mapped_column(
        "flgest", String(length=STATUS_FLAG_MAX_LENGTH)
    )
    storage_code: Mapped[str] = mapped_column(
        "codalm", String(length=STORAGE_CODE_MAX_LENGTH)
    )
    user_id: Mapped[str] = mapped_column("idusers", String(length=USER_ID_MAX_LENGTH))
    flgatc: Mapped[str] = mapped_column("flgatc", String(length=FLGACT_MAX_LENGTH))
    flgprt: Mapped[str] = mapped_column(
        "flgprt", String(length=PRINTED_FLAG_MAX_LENGTH)
    )
    status_param_id: Mapped[int] = mapped_column("status_param_id", default=1023)

    detail = relationship(
        "ServiceOrderDetail",
        lazy="noload",
        primaryjoin=lambda: and_(
            ServiceOrder.company_code == ServiceOrderDetail.company_code,
            ServiceOrder._type == ServiceOrderDetail.order_type,
            ServiceOrder.id == ServiceOrderDetail.order_id,
        ),
        single_parent=True,
        viewonly=True,
        foreign_keys=lambda: [
            ServiceOrderDetail.company_code,
            ServiceOrderDetail.order_type,
            ServiceOrderDetail.order_id,
        ],
    )

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "nroos", "tpoos"),
        {"schema": "PUB"},
    )


class ServiceOrderDetail(PromecBase):
    __tablename__ = "opedosmp"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    order_id: Mapped[str] = mapped_column(
        "nroos", String(length=SERVICE_ORDER_ID_MAX_LENGTH)
    )
    order_type: Mapped[str] = mapped_column(
        "tpoos", String(length=SERVICE_ORDER_TYPE_MAX_LENGTH)
    )
    product_id: Mapped[str] = mapped_column(
        "codprod", String(length=PRODUCT_CODE_MAX_LENGTH)
    )
    quantity_ordered: Mapped[float] = mapped_column("canord")
    quantity_supplied: Mapped[float] = mapped_column("canate")
    price: Mapped[float] = mapped_column("precto")
    status_param_id: Mapped[int] = mapped_column("status_param_id", default=1)

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "nroos", "tpoos", "codprod"),
        {"schema": "PUB"},
    )


class SupplierArrivalPort(PromecBase):
    __tablename__ = "prollegada"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    nrodir: Mapped[str] = mapped_column("nrodir", String(length=NRODIR_MAX_LENGTH))
    address: Mapped[str] = mapped_column(
        "dirpro", String(length=SUPPLIER_ADDRESS_MAX_LENGTH)
    )
    supplier_id: Mapped[str] = mapped_column(
        "codpro", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "codpro", "nrodir"),
        {"schema": "PUB"},
    )


class ServiceOrderStock(PromecBase):
    __tablename__ = "almstkserv"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    period: Mapped[int] = mapped_column("periodo")
    product_code: Mapped[str] = mapped_column(
        "codprod", String(length=PRODUCT_CODE_MAX_LENGTH)
    )
    reference_number: Mapped[str] = mapped_column(
        "refnro", String(length=REFERENCE_NUMBER_MAX_LENGTH)
    )
    storage_code: Mapped[str] = mapped_column(
        "codalm", String(length=STORAGE_CODE_MAX_LENGTH)
    )
    item_number: Mapped[int] = mapped_column("nroitm")
    stkact: Mapped[float] = mapped_column("stkact")
    provided_quantity: Mapped[float] = mapped_column("provided_quantity")
    supplier_yarn_id: Mapped[str] = mapped_column(
        "proveedor_hilado_id", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    dispatch_id: Mapped[str] = mapped_column(
        "numero_salida", String(length=EXIT_NUMBER_MAX_LENGTH)
    )
    is_complement: Mapped[bool] = mapped_column("es_complemento", default=False)
    status_flag: Mapped[str] = mapped_column(
        "flgest", String(length=STATUS_FLAG_MAX_LENGTH)
    )
    supplier_code: Mapped[str] = mapped_column(
        "codprov", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    creation_date: Mapped[date] = mapped_column("fchdoc")
    pormer: Mapped[float] = mapped_column("pormer")
    quantity_received: Mapped[float] = mapped_column("canting")
    quantity_dispatched: Mapped[float] = mapped_column("cantsal")

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "codprod", "refnro", "nroitm"),
        {"schema": "PUB"},
    )


class Movement(PromecBase):
    __tablename__ = "almcmovi"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    storage_code: Mapped[str] = mapped_column(
        "codalm", String(length=STORAGE_CODE_MAX_LENGTH)
    )
    movement_type: Mapped[str] = mapped_column(
        "tpomov", String(length=MOVEMENT_TYPE_MAX_LENGTH)
    )
    movement_code: Mapped[str] = mapped_column(
        "codmov", String(length=MOVEMENT_CODE_MAX_LENGTH)
    )
    document_code: Mapped[str] = mapped_column(
        "coddoc", String(length=DOCUMENT_CODE_MAX_LENGTH)
    )
    document_number: Mapped[str] = mapped_column(
        "nrodoc", String(length=DOCUMENT_NUMBER_MAX_LENGTH)
    )
    period: Mapped[int] = mapped_column("periodo")
    creation_date: Mapped[date] = mapped_column("fchdoc")
    creation_time: Mapped[str] = mapped_column("horadoc")
    currency_code: Mapped[int] = mapped_column("codmon", default=1)
    exchange_rate: Mapped[float] = mapped_column("tpocmb", default=0.0)
    document_note: Mapped[str] = mapped_column(
        "notadoc", String(length=DOCUMENT_NOTE_MAX_LENGTH), default=""
    )
    clfaux: Mapped[str] = mapped_column("clfaux", String(length=CLFAUX_MAX_LENGTH))
    auxiliary_code: Mapped[str] = mapped_column(
        "codaux", String(length=AUXILIARY_CODE_MAX_LENGTH)
    )
    status_flag: Mapped[str] = mapped_column(
        "flgest", String(length=STATUS_FLAG_MAX_LENGTH)
    )
    user_id: Mapped[str] = mapped_column("idusers", String(length=USER_ID_MAX_LENGTH))
    auxiliary_name: Mapped[str] = mapped_column(
        "nomaux", String(length=AUXILIARY_NAME_MAX_LENGTH)
    )
    reference_document: Mapped[str] = mapped_column(
        "refdoc", String(length=REFERENCE_DOCUMENT_MAX_LENGTH)
    )
    reference_number1: Mapped[str] = mapped_column(
        "nroref", String(length=REFERENCE_NUMBER_MAX_LENGTH)
    )
    reference_number2: Mapped[str] = mapped_column(
        "refnro", String(length=REFERENCE_NUMBER_MAX_LENGTH)
    )
    nrogf: Mapped[str] = mapped_column(
        "nrogf", String(length=NROGF_MAX_LENGTH)
    )  # //! Definir nombre representativo
    sergf: Mapped[str] = mapped_column(
        "sergf", String(length=SERGF_MAX_LENGTH)
    )  # //! Definir nombre representativo
    fecgf: Mapped[date] = mapped_column("fecgf")  # //! Definir nombre representativo
    origmov: Mapped[str] = mapped_column("origmov", String(length=ORIGMOV_MAX_LENGTH))
    annulment_date: Mapped[date] = mapped_column("fchanu")
    annulment_user_id: Mapped[str] = mapped_column(
        "userid_a", String(length=ANNULMENT_USER_ID_MAX_LENGTH)
    )
    transporter_code: Mapped[str] = mapped_column(
        "codtransp", String(length=TRANSPORTER_CODE_MAX_LENGTH)
    )
    reference_code: Mapped[str] = mapped_column(
        "codref", String(length=REFERENCE_CODE_MAX_LENGTH)
    )
    serial_number: Mapped[str] = mapped_column(
        "nroser", String(length=SERIAL_NUMBER_MAX_LENGTH)
    )
    printed_flag: Mapped[str] = mapped_column(
        "flgprt", String(length=PRINTED_FLAG_MAX_LENGTH)
    )
    flgact: Mapped[str] = mapped_column("flgact", String(length=FLGACT_MAX_LENGTH))
    nrodir1: Mapped[str] = mapped_column(
        "nrodir", String(length=INGRESS_NUMBER_MAX_LENGTH)
    )  # //! Definir nombre representativo
    transaction_motive: Mapped[str] = mapped_column(
        "mottras", String(length=TRANSACTION_MOTIVE_MAX_LENGTH)
    )
    flgtras: Mapped[bool] = mapped_column(
        "flgtras", default=False
    )  # //! Definir nombre representativo
    empqnro2: Mapped[str] = mapped_column(
        "empqnro2", String(length=EMPQNRO2_MAX_LENGTH)
    )
    flgreclamo: Mapped[str] = mapped_column(
        "flgreclamo", String(length=FLGRECLAMO_MAX_LENGTH)
    )
    flgsit: Mapped[str] = mapped_column("flgsit", String(length=FLGSIT_MAX_LENGTH))
    servadi: Mapped[str] = mapped_column("servadi", String(length=SERVADI_MAX_LENGTH))
    tarfservadi: Mapped[float] = mapped_column("tarfservadi")
    voucher_number: Mapped[str] = mapped_column(
        "nrovou", String(length=VOUCHER_NUMBER_MAX_LENGTH)
    )
    fchcp: Mapped[date] = mapped_column("fchcp")
    flgcbd: Mapped[str] = mapped_column("flgcbd", String(length=FLGCBD_MAX_LENGTH))
    nrodir2: Mapped[str] = mapped_column(
        "nrodir1", String(length=INGRESS_NUMBER_MAX_LENGTH)
    )  # //! Definir nombre representativo
    origin_station: Mapped[str] = mapped_column(
        "estacion", String(length=ORIGIN_STATION_MAX_LENGTH)
    )
    undpesobrutototal: Mapped[str] = mapped_column(
        "undpesobrutototal", String(length=UNDPESOBRUTOTOTAL_MAX_LENGTH)
    )
    transaction_mode: Mapped[str] = mapped_column(
        "modtrans", String(length=TRANSACTION_MODE_MAX_LENGTH)
    )
    driver_code: Mapped[str] = mapped_column(
        "codchof", String(length=DRIVER_CODE_MAX_LENGTH)
    )
    vehicle_code: Mapped[str] = mapped_column(
        "codveh", String(length=VEHICLE_CODE_MAX_LENGTH)
    )
    vehicle_brand: Mapped[str] = mapped_column(
        "marcaveh", String(length=VEHICLE_BRAND_MAX_LENGTH)
    )
    vehicle_plate: Mapped[str] = mapped_column(
        "placa", String(length=VEHICLE_PLATE_MAX_LENGTH)
    )
    driver_license: Mapped[str] = mapped_column(
        "licencia", String(length=DRIVER_LICENSE_MAX_LENGTH)
    )
    flgele: Mapped[str] = mapped_column("flgele", String(length=FLGELE_MAX_LENGTH))
    prefele: Mapped[str] = mapped_column("prefele", String(length=PREFELE_MAX_LENGTH))
    intentosenvele: Mapped[int] = mapped_column("intentosenvele")
    supplier_batch: Mapped[str] = mapped_column(
        "loteprov", String(length=SUPPLIER_BATCH_MAX_LENGTH)
    )
    mecsa_batch: Mapped[str] = mapped_column(
        "lotem", String(length=MECSA_BATCH_MAX_LENGTH)
    )
    fchinitras: Mapped[date] = mapped_column(
        "fchinitras"
    )  # //! Definir nombre representativo
    hashcode: Mapped[str] = mapped_column(
        "hashcode",
        String(length=HASHCODE_MAX_LENGTH),
    )

    purchase_order = relationship(
        "OrdenCompra",
        lazy="noload",
        primaryjoin=lambda: and_(
            Movement.company_code == OrdenCompra.company_code,
            Movement.reference_number2 == OrdenCompra.purchase_order_number,
        ),
        # back_populates="movement",
        uselist=False,
        foreign_keys=lambda: [
            OrdenCompra.company_code,
            OrdenCompra.purchase_order_number,
        ],
    )

    detail = relationship(
        "MovementDetail",
        lazy="noload",
        cascade="",
        primaryjoin=lambda: and_(
            Movement.company_code == MovementDetail.company_code,
            Movement.storage_code == MovementDetail.storage_code,
            Movement.movement_type == MovementDetail.movement_type,
            Movement.movement_code == MovementDetail.movement_code,
            Movement.document_code == MovementDetail.document_code,
            Movement.document_number == MovementDetail.document_number,
            Movement.period == MovementDetail.period,
        ),
        back_populates="movement",
        single_parent=True,
        viewonly=True,
        foreign_keys=lambda: [
            MovementDetail.company_code,
            MovementDetail.storage_code,
            MovementDetail.movement_type,
            MovementDetail.movement_code,
            MovementDetail.document_code,
            MovementDetail.document_number,
            MovementDetail.period,
        ],
    )

    detail_dyeing = relationship(
        "FabricWarehouse",
        lazy="noload",
        primaryjoin=lambda: and_(
            Movement.company_code == FabricWarehouse.company_code,
            Movement.document_number == FabricWarehouse.document_number,
        ),
        single_parent=True,
        viewonly=True,
        foreign_keys=lambda: [
            FabricWarehouse.company_code,
            FabricWarehouse.document_number,
        ],
    )

    __table_args__ = (
        PrimaryKeyConstraint(
            "codcia", "codalm", "tpomov", "codmov", "coddoc", "nrodoc", "periodo"
        ),
        {"schema": "PUB"},
    )

    def __repr__(self):
        return (
            f"<Movement(\n"
            f"    codcia={self.company_code},\n"
            f"    codalm={self.storage_code},\n"
            f"    tpomov={self.movement_type},\n"
            f"    codmov={self.movement_code},\n"
            f"    coddoc={self.document_code},\n"
            f"    nrodoc={self.document_number},\n"
            f"    periodo={self.period}\n"
            f"    creation_date={self.creation_date},\n"
            f"    creation_time={self.creation_time},\n"
            f"    currency_code={self.currency_code},\n"
            f"    exchange_rate={self.exchange_rate},\n"
            f"    document_note={self.document_note},\n"
            f"    clfaux={self.clfaux},\n"
            f"    auxiliary_code={self.auxiliary_code},\n"
            f"    status_flag={self.status_flag},\n"
            f"    user_id={self.user_id},\n"
            f"    auxiliary_name={self.auxiliary_name},\n"
            f"    reference_document={self.reference_document},\n"
            f"    reference_number2={self.reference_number2},\n"
            f"    nrogf={self.nrogf},\n"
            f"    sergf={self.sergf},\n"
            f"    fecgf={self.fecgf},\n"
            f"    origmov={self.origmov},\n"
            f"    annulment_date={self.annulment_date},\n"
            f"    annulment_user_id={self.annulment_user_id},\n"
            f"    serial_number={self.serial_number},\n"
            f"    printed_flag={self.printed_flag},\n"
            f"    flgact={self.flgact},\n"
            f"    flgtras={self.flgtras},\n"
            f"    flgreclamo={self.flgreclamo},\n"
            f"    flgsit={self.flgsit},\n"
            f"    voucher_number={self.voucher_number},\n"
            f"    servadi={self.servadi},\n"
            f"    tarfservadi={self.tarfservadi},\n"
            f"    fchcp={self.fchcp},\n"
            f"    flgcbd={self.flgcbd},\n"
            f"    origin_station={self.origin_station},\n"
            f"    undpesobrutototal={self.undpesobrutototal},\n"
            f"    transaction_mode={self.transaction_mode},\n"
            f"    intentosenvele={self.intentosenvele},\n"
            f"    supplier_batch={self.supplier_batch},\n"
            f"    mecsa_batch={self.mecsa_batch}\n"
            f")>"
        )


class MovementDetail(PromecBase):
    __tablename__ = "almdmovi"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    storage_code: Mapped[str] = mapped_column(
        "codalm", String(length=STORAGE_CODE_MAX_LENGTH)
    )
    movement_type: Mapped[str] = mapped_column(
        "tpomov", String(length=MOVEMENT_TYPE_MAX_LENGTH)
    )
    movement_code: Mapped[str] = mapped_column(
        "codmov", String(length=MOVEMENT_CODE_MAX_LENGTH)
    )
    document_code: Mapped[str] = mapped_column(
        "coddoc", String(length=DOCUMENT_CODE_MAX_LENGTH)
    )
    document_number: Mapped[str] = mapped_column(
        "nrodoc", String(length=DOCUMENT_NUMBER_MAX_LENGTH)
    )
    item_number: Mapped[int] = mapped_column("nroitm")
    period: Mapped[int] = mapped_column("periodo")
    creation_date: Mapped[date] = mapped_column("fchdoc")
    creation_time: Mapped[str] = mapped_column("horadoc")
    product_code: Mapped[str] = mapped_column(
        "codprod", String(length=PRODUCT_CODE_MAX_LENGTH)
    )
    unit_code: Mapped[str] = mapped_column(
        "codund", String(length=UNIT_CODE_MAX_LENGTH)
    )
    factor: Mapped[int] = mapped_column("factor")
    mecsa_weight: Mapped[float] = mapped_column("cantidad")
    guide_gross_weight: Mapped[float] = mapped_column("pesobrtoguia")
    precto: Mapped[float] = mapped_column("precto")  # //! Definir nombre representativo
    impcto: Mapped[float] = mapped_column("impcto")  # //! Definir nombre representativo
    currency_code: Mapped[int] = mapped_column("codmon", default=1)
    exchange_rate: Mapped[float] = mapped_column("tpocmb", default=0.0)
    impmn1: Mapped[float] = mapped_column("impmn1")  # //! Definir nombre representativo
    impmn2: Mapped[float] = mapped_column("impmn2")  # //! Definir nombre representativo
    stkgen: Mapped[float] = mapped_column("stkgen")
    stkalm: Mapped[float] = mapped_column("stkalm")
    ctomn1: Mapped[float] = mapped_column("ctomn1")  # //! Definir nombre representativo
    ctomn2: Mapped[float] = mapped_column("ctomn2")  # //! Definir nombre representativo
    status_flag: Mapped[str] = mapped_column(
        "flgest", String(length=STATUS_FLAG_MAX_LENGTH)
    )
    is_weighted: Mapped[bool] = mapped_column("flgpesaje")
    entry_group_number: Mapped[int] = mapped_column("nrogrupoingr")
    entry_item_number: Mapped[int] = mapped_column("nroitemingr")
    reference_code: Mapped[str] = mapped_column(
        "codref", String(length=REFERENCE_CODE_MAX_LENGTH)
    )
    reference_number: Mapped[str] = mapped_column(
        "nroref", String(length=REFERENCE_NUMBER_MAX_LENGTH)
    )
    nrotarj: Mapped[str] = mapped_column(
        "nrotarj", String(length=NROTARJ_MAX_LENGTH)
    )  # //! Definir nombre representativo
    nroreq: Mapped[str] = mapped_column(
        "nroreq", String(length=NROREQ_MAX_LENGTH)
    )  # //! Definir nombre representativo
    detdoc: Mapped[str] = mapped_column("detdoc", String(length=DETDOC_MAX_LENGTH))
    supplier_batch: Mapped[str] = mapped_column(
        "loteprov", String(length=SUPPLIER_BATCH_MAX_LENGTH)
    )
    movement = relationship(
        "Movement",
        lazy="noload",
        viewonly=True,
        primaryjoin=lambda: and_(
            Movement.company_code == MovementDetail.company_code,
            Movement.storage_code == MovementDetail.storage_code,
            Movement.movement_type == MovementDetail.movement_type,
            Movement.movement_code == MovementDetail.movement_code,
            Movement.document_code == MovementDetail.document_code,
            Movement.document_number == MovementDetail.document_number,
            Movement.period == MovementDetail.period,
        ),
        back_populates="detail",
        foreign_keys=lambda: [
            MovementDetail.company_code,
            MovementDetail.storage_code,
            MovementDetail.movement_type,
            MovementDetail.movement_code,
            MovementDetail.document_code,
            MovementDetail.document_number,
            MovementDetail.period,
        ],
    )

    movement_ingress = relationship(
        "MovementYarnOCHeavy",
        viewonly=True,
        lazy="noload",
        primaryjoin=lambda: and_(
            MovementDetail.company_code == MovementYarnOCHeavy.company_code,
            MovementDetail.reference_number == MovementYarnOCHeavy.ingress_number,
            MovementDetail.entry_group_number == MovementYarnOCHeavy.group_number,
            MovementDetail.entry_item_number == MovementYarnOCHeavy.item_number,
        ),
        uselist=False,
        foreign_keys=lambda: [
            MovementYarnOCHeavy.company_code,
            MovementYarnOCHeavy.ingress_number,
            MovementYarnOCHeavy.group_number,
            MovementYarnOCHeavy.item_number,
        ],
    )

    detail_aux = relationship(
        "MovementDetailAux",
        lazy="noload",
        cascade="",
        viewonly=True,
        primaryjoin=lambda: and_(
            MovementDetail.company_code == MovementDetailAux.company_code,
            MovementDetail.document_code == MovementDetailAux.document_code,
            MovementDetail.document_number == MovementDetailAux.document_number,
            MovementDetail.item_number == MovementDetailAux.item_number,
        ),
        back_populates="movement_detail",
        uselist=False,
        foreign_keys=lambda: [
            MovementDetailAux.company_code,
            MovementDetailAux.document_code,
            MovementDetailAux.document_number,
            MovementDetailAux.item_number,
        ],
    )

    detail_fabric = relationship(
        "FabricWarehouse",
        lazy="noload",
        viewonly=True,
        primaryjoin=lambda: and_(
            MovementDetail.company_code == FabricWarehouse.company_code,
            MovementDetail.document_number == FabricWarehouse.document_number,
            MovementDetail.product_code == FabricWarehouse.product_id,
        ),
        uselist=False,
        foreign_keys=lambda: [
            FabricWarehouse.company_code,
            FabricWarehouse.document_number,
            FabricWarehouse.fabric_id,
        ],
    )

    detail_card = relationship(
        "CardOperation",
        lazy="noload",
        viewonly=True,
        primaryjoin=lambda: (
            func.concat(MovementDetail.document_code, MovementDetail.document_number)
            == CardOperation.document_number
        ),
        single_parent=True,
        foreign_keys=lambda: [
            CardOperation.document_number,
        ],
    )

    detail_heavy = relationship(
        "MovementYarnOCHeavy",
        viewonly=True,
        lazy="noload",
        primaryjoin=lambda: and_(
            MovementDetail.company_code == MovementYarnOCHeavy.company_code,
            MovementDetail.document_number == MovementYarnOCHeavy.ingress_number,
            MovementDetail.item_number == MovementYarnOCHeavy.item_number,
        ),
        foreign_keys=lambda: [
            MovementYarnOCHeavy.company_code,
            MovementYarnOCHeavy.ingress_number,
            MovementYarnOCHeavy.item_number,
        ],
    )

    yarn = relationship(
        "InventoryItem",
        lazy="noload",
        primaryjoin=lambda: and_(
            MovementDetail.company_code == InventoryItem.company_code,
            MovementDetail.product_code == InventoryItem.id,
        ),
        foreign_keys=lambda: [MovementDetail.company_code, MovementDetail.product_code],
        viewonly=True,
    )

    __table_args__ = (
        PrimaryKeyConstraint(
            "codcia",
            "periodo",
            "codalm",
            "tpomov",
            "codmov",
            "coddoc",
            "nrodoc",
            "nroitm",
        ),
        {"schema": "PUB"},
    )

    def __repr__(self):
        return (
            f"<MovementDetail(\n"
            f"    codcia={self.company_code},\n"
            f"    codalm={self.storage_code},\n"
            f"    tpomov={self.movement_type},\n"
            f"    codmov={self.movement_code},\n"
            f"    coddoc={self.document_code},\n"
            f"    nrodoc={self.document_number},\n"
            f"    nroitm={self.item_number},\n"
            f"    periodo={self.period},\n"
            f"    creation_date={self.creation_date},\n"
            f"    creation_time={self.creation_time},\n"
            f"    codprod={self.product_code},\n"
            f"    codund={self.unit_code},\n"
            f"    factor={self.factor},\n"
            f"    mecsa_weight={self.mecsa_weight},\n"
            f"    guide_gross_weight={self.guide_gross_weight},\n"
            f"    precto={self.precto},\n"
            f"    impcto={self.impcto},\n"
            f"    currency_code={self.currency_code},\n"
            f"    exchange_rate={self.exchange_rate},\n"
            f"    impmn1={self.impmn1},\n"
            f"    impmn2={self.impmn2},\n"
            f"    stkgen={self.stkgen},\n"
            f"    stkalm={self.stkalm},\n"
            f"    ctomn1={self.ctomn1},\n"
            f"    ctomn2={self.ctomn2},\n"
            f"    status_flag={self.status_flag},\n"
            f"    is_weighted={self.is_weighted}\n"
            f"    nrotarj={self.nrotarj},\n"
            f")>"
        )


class MovementDetailAux(PromecBase):
    __tablename__ = "detauxmov"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    document_code: Mapped[str] = mapped_column(
        "movdoc", String(length=DOCUMENT_CODE_MAX_LENGTH)
    )
    document_number: Mapped[str] = mapped_column(
        "movnro", String(length=DOCUMENT_NUMBER_MAX_LENGTH)
    )
    item_number: Mapped[int] = mapped_column("nroitm")
    period: Mapped[int] = mapped_column("periodo")
    product_code: Mapped[str] = mapped_column(
        "codprod", String(length=PRODUCT_CODE_MAX_LENGTH)
    )
    unit_code: Mapped[str] = mapped_column(
        "codund", String(length=UNIT_CODE_MAX_LENGTH)
    )
    factor: Mapped[int] = mapped_column("factor")
    precto: Mapped[float] = mapped_column("precto")
    impcto: Mapped[float] = mapped_column("impcto")
    creation_date: Mapped[date] = mapped_column("fchemi")
    mecsa_weight: Mapped[float] = mapped_column("pesoneto")
    guide_net_weight: Mapped[float] = mapped_column("pesobrto")
    guide_cone_count: Mapped[int] = mapped_column("nroconos")
    guide_package_count: Mapped[int] = mapped_column("nrobolsas")
    reference_code: Mapped[str] = mapped_column(
        "codref", String(length=REFERENCE_CODE_MAX_LENGTH)
    )
    mecsa_batch: Mapped[str] = mapped_column(
        "lotem", String(length=MECSA_BATCH_MAX_LENGTH)
    )
    supplier_batch: Mapped[str] = mapped_column(
        "lotep", String(length=SUPPLIER_BATCH_MAX_LENGTH)
    )
    reference_number: Mapped[str] = mapped_column(
        "nroref", String(length=REFERENCE_NUMBER_MAX_LENGTH)
    )
    group_number: Mapped[str] = mapped_column(
        "grupo", String(length=GROUP_NUMBER_MAX_LENGTH)
    )
    movement_detail = relationship(
        "MovementDetail",
        lazy="noload",
        primaryjoin=lambda: and_(
            MovementDetail.company_code == MovementDetailAux.company_code,
            MovementDetail.document_code == MovementDetailAux.document_code,
            MovementDetail.document_number == MovementDetailAux.document_number,
            MovementDetail.item_number == MovementDetailAux.item_number,
        ),
        back_populates="detail_aux",
        foreign_keys=lambda: [
            MovementDetailAux.company_code,
            MovementDetailAux.document_code,
            MovementDetailAux.document_number,
            MovementDetailAux.item_number,
        ],
    )

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "movdoc", "movnro", "nroitm", "periodo"),
        {"schema": "PUB"},
    )


class MovementYarnOCHeavy(PromecBase):
    __tablename__ = "opehilado"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    yarn_id: Mapped[str] = mapped_column(
        "codprod", String(length=PRODUCT_CODE_MAX_LENGTH)
    )
    group_number: Mapped[str] = mapped_column(
        "grupo", String(length=GROUP_NUMBER_MAX_LENGTH)
    )
    ingress_number: Mapped[str] = mapped_column(
        "nroing", String(length=INGRESS_NUMBER_MAX_LENGTH)
    )
    item_number: Mapped[int] = mapped_column("nroitm")
    exit_number: Mapped[str] = mapped_column(
        "nrosal", String(length=EXIT_NUMBER_MAX_LENGTH), default=""
    )
    #  ProHil
    supplier_yarn_id: Mapped[str] = mapped_column(
        "prohil", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    status_flag: Mapped[str] = mapped_column(
        "flgest", String(length=STATUS_FLAG_MAX_LENGTH)
    )
    entry_user_id: Mapped[str] = mapped_column(
        "idusers_i", String(length=USER_ID_MAX_LENGTH)
    )
    exit_user_id: Mapped[str] = mapped_column(
        "idusers_s", String(length=USER_ID_MAX_LENGTH)
    )
    cone_count: Mapped[int] = mapped_column("nroconos")
    package_count: Mapped[int] = mapped_column("nrobolsas")
    destination_storage: Mapped[str] = mapped_column(
        "almdes", String(length=STORAGE_CODE_MAX_LENGTH)
    )
    net_weight: Mapped[float] = mapped_column("pesoneto")
    gross_weight: Mapped[float] = mapped_column("pesobrto")
    dispatch_status: Mapped[bool] = mapped_column("flgdesp")
    packages_left: Mapped[int] = mapped_column("nrobolsasrest")
    cones_left: Mapped[int] = mapped_column("nroconosrest")

    supplier_batch: Mapped[str] = mapped_column(
        "loteprov", String(length=SUPPLIER_BATCH_MAX_LENGTH)
    )
    movement_detail = relationship(
        "MovementDetail",
        lazy="noload",
        viewonly=True,
        primaryjoin=lambda: and_(
            MovementYarnOCHeavy.company_code == MovementDetail.company_code,
            YARN_PURCHASE_ENTRY_STORAGE_CODE == MovementDetail.storage_code,
            YARN_PURCHASE_ENTRY_MOVEMENT_TYPE == MovementDetail.movement_type,
            YARN_PURCHASE_ENTRY_MOVEMENT_CODE == MovementDetail.movement_code,
            YARN_PURCHASE_ENTRY_DOCUMENT_CODE == MovementDetail.document_code,
            MovementYarnOCHeavy.ingress_number == MovementDetail.document_number,
            MovementYarnOCHeavy.item_number == MovementDetail.item_number,
        ),
        uselist=False,
        foreign_keys=lambda: [
            MovementDetail.company_code,
            MovementDetail.document_number,
            MovementDetail.item_number,
            MovementDetail.storage_code,
            MovementDetail.movement_type,
            MovementDetail.movement_code,
            MovementDetail.document_code,
        ],
    )

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "codprod", "grupo", "nroitm", "nroing"),
        {"schema": "PUB"},
    )

    def __repr__(self):
        return (
            f"<MovementYarnOCHeavy(\n"
            f"    codcia={self.company_code},\n"
            f"    codprod={self.yarn_id},\n"
            f"    grupo={self.group_number},\n"
            f"    nroing={self.ingress_number},\n"
            f"    nroitm={self.item_number},\n"
            f"    nrosal={self.exit_number},\n"
            f"    flgest={self.status_flag},\n"
            f"    nroconos={self.cone_count},\n"
            f"    nrobolsas={self.package_count},\n"
            f"    pesoneto={self.net_weight},\n"
            f"    pesobrto={self.gross_weight},\n"
            f"    flgdesp={self.dispatch_status},\n"
            f"    nrobolsasrest={self.packages_left}\n"
            f")>"
        )


class FabricWarehouse(PromecBase):
    __tablename__ = "almtejido"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )

    fabric_id: Mapped[str] = mapped_column(
        "codtej", String(length=FABRIC_ID_MAX_LENGTH)
    )
    width: Mapped[float] = mapped_column("ancho")
    codcol: Mapped[str] = mapped_column("codcol", String(length=CODCOL_MAX_LENGTH))
    guide_net_weight: Mapped[float] = mapped_column("pesoguia")
    mecsa_weight: Mapped[float] = mapped_column("pesomecsa")
    document_number: Mapped[str] = mapped_column(
        "nrodoc", String(length=DOCUMENT_NUMBER_MAX_LENGTH)
    )
    creation_date: Mapped[date] = mapped_column("fchdoc")
    status_flag: Mapped[str] = mapped_column(
        "flgest", String(length=STATUS_FLAG_MAX_LENGTH)
    )
    product_id: Mapped[str] = mapped_column(
        "codprod", String(length=PRODUCT_CODE_MAX_LENGTH)
    )
    document_code: Mapped[str] = mapped_column(
        "coddoc", String(length=DOCUMENT_CODE_MAX_LENGTH)
    )
    roll_count: Mapped[int] = mapped_column("nrorollos")
    meters_count: Mapped[float] = mapped_column("nromet")
    density: Mapped[float] = mapped_column("densidad")
    real_width: Mapped[float] = mapped_column("anchoreal")
    yarn_supplier_id: Mapped[str] = mapped_column(
        "prohil", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    service_order_id: Mapped[str] = mapped_column(
        "nroserv", String(length=SERVICE_ORDER_ID_MAX_LENGTH)
    )
    tint_supplier_id: Mapped[str] = mapped_column(
        "protin", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    fabric_type: Mapped[str] = mapped_column(
        "tpotej", String(length=FABRIC_TYPE_MAX_LENGTH)
    )
    tint_color_id: Mapped[str] = mapped_column(
        "coltin", String(length=COLOR_ID_MAX_LENGTH)
    )
    _tint_supplier_color_id: Mapped[str] = mapped_column(
        "colpro", String(length=COLOR_ID_MAX_LENGTH)
    )
    tint_supplier_color_id: Mapped[str] = mapped_column(
        "protincol", String(length=COLOR_ID_MAX_LENGTH)
    )

    idavctint: Mapped[str] = mapped_column(default="")

    detail_card = relationship(
        "CardOperation",
        lazy="noload",
        primaryjoin=lambda: and_(
            FabricWarehouse.company_code == CardOperation.company_code,
            func.concat(FabricWarehouse.document_code, FabricWarehouse.document_number)
            == CardOperation.exit_number,
        ),
        single_parent=True,
        viewonly=True,
        foreign_keys=lambda: [
            CardOperation.company_code,
            CardOperation.document_number,
        ],
    )

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "coddoc", "codprod", "nrodoc"),
        {"schema": "PUB"},
    )


class ServiceCardOperation(PromecBase):
    __tablename__ = "opetarserv"
    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    period: Mapped[int] = mapped_column("periodo")
    serial_code: Mapped[str] = mapped_column(
        "codser", String(length=SERIAL_NUMBER_MAX_LENGTH)
    )
    supplier_id: Mapped[str] = mapped_column(
        "codpro", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    codcol: Mapped[str] = mapped_column("codcol", String(length=CODCOL_MAX_LENGTH))
    fabric_id: Mapped[str] = mapped_column(
        "codtej", String(length=FABRIC_ID_MAX_LENGTH)
    )
    width: Mapped[float] = mapped_column("ancho")
    rate: Mapped[float] = mapped_column("tarifa")
    extended_rate: Mapped[float] = mapped_column("tarifal")
    month_number: Mapped[int] = mapped_column("nromes")

    __table_args__ = (
        PrimaryKeyConstraint(
            "codcia",
            "codser",
            "codpro",
            "codcol",
            "codtej",
            "ancho",
            "periodo",
            "nromes",
        ),
    )


class CardOperation(PromecBase):
    __tablename__ = "opetarjeta"

    id: Mapped[str] = mapped_column("nrotarj", String(length=CARD_ID_MAX_LENGTH))
    fabric_id: Mapped[str] = mapped_column(
        "codtej", String(length=FABRIC_ID_MAX_LENGTH)
    )
    width: Mapped[float] = mapped_column("ancho")
    codcol: Mapped[str] = mapped_column("codcol", String(length=CODCOL_MAX_LENGTH))
    net_weight: Mapped[float] = mapped_column("pesoneto")
    gross_weight: Mapped[float] = mapped_column("pesobrto")
    document_number: Mapped[str] = mapped_column(
        "nrodoc", String(length=DOCUMENT_NUMBER_MAX_LENGTH)
    )
    creation_date: Mapped[date] = mapped_column("fching")
    supplier_weaving_tej: Mapped[str] = mapped_column(
        "protej", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    status_flag: Mapped[str] = mapped_column(
        "flgest", String(length=STATUS_FLAG_MAX_LENGTH)
    )
    storage_code: Mapped[str] = mapped_column(
        "codalm", String(length=STORAGE_CODE_MAX_LENGTH)
    )
    entry_user_id: Mapped[str] = mapped_column(
        "idusers_i", String(length=USER_ID_MAX_LENGTH)
    )
    exit_user_id: Mapped[str] = mapped_column(
        "idusers_s", String(length=USER_ID_MAX_LENGTH)
    )
    tint_user_id: Mapped[str] = mapped_column(
        "idusers_t", String(length=USER_ID_MAX_LENGTH)
    )
    product_id: Mapped[str] = mapped_column(
        "codprod", String(length=PRODUCT_CODE_MAX_LENGTH)
    )
    exit_number: Mapped[str] = mapped_column(
        "nrosal", String(length=EXIT_NUMBER_MAX_LENGTH), default=""
    )
    fabric_type: Mapped[str] = mapped_column(
        "tpotej", String(length=FABRIC_TYPE_MAX_LENGTH)
    )
    tint_supplier_id: Mapped[str] = mapped_column(
        "protin", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    tint_color_id: Mapped[str] = mapped_column(
        "coltin", String(length=COLOR_ID_MAX_LENGTH)
    )
    desttej: Mapped[str] = mapped_column("desttej", String(length=DESTTEJ_MAX_LENGTH))
    flgsit: Mapped[str] = mapped_column("flgsit", String(length=FLGSIT_MAX_LENGTH))
    sdoneto: Mapped[float] = mapped_column("sdoneto")
    yarn_supplier_id: Mapped[str] = mapped_column(
        "prohil", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    service_order_id: Mapped[str] = mapped_column(
        "nroserv", String(length=SERVICE_ORDER_ID_MAX_LENGTH)
    )
    card_type: Mapped[str] = mapped_column(
        "tpotar", String(length=CARD_TYPE_MAX_LENGTH)
    )
    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    period: Mapped[int] = mapped_column("periodo")

    __table_args__ = (
        PrimaryKeyConstraint("nrotarj"),
        {"schema": "PUB"},
    )


class Supplier(PromecBase):
    __tablename__ = "proveedor"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    code: Mapped[str] = mapped_column("codpro", String(length=SUPPLIER_CODE_MAX_LENGTH))
    name: Mapped[str] = mapped_column("nompro", String(length=SUPPLIER_NAME_MAX_LENGTH))
    address: Mapped[str] = mapped_column(
        "dirpro", String(length=SUPPLIER_ADDRESS_MAX_LENGTH)
    )
    ruc: Mapped[str] = mapped_column("rucpro", String(length=SUPPLIER_RUC_MAX_LENGTH))
    is_active: Mapped[str] = mapped_column(
        "condicion", String(length=ACTIVE_STATUS_PROMEC)
    )
    storage_code: Mapped[str] = mapped_column(
        "codalm", String(length=STORAGE_CODE_MAX_LENGTH)
    )
    _email: Mapped[str] = mapped_column("e-mail", String(length=EMAIL_MAX_LENGTH))
    email: Mapped[str] = column_property(
        func.substr(
            _email,
            literal_column("1"),
            literal_column("255"),
        )
    )
    initials: Mapped[str] = mapped_column(
        "iniciales", String(length=INITIALS_MAX_LENGTH)
    )

    other_addresses = relationship(
        "SupplierArrivalPort",
        lazy="noload",
        primaryjoin=lambda: and_(
            Supplier.company_code == SupplierArrivalPort.company_code,
            Supplier.code == SupplierArrivalPort.supplier_id,
        ),
        foreign_keys=lambda: [
            SupplierArrivalPort.company_code,
            SupplierArrivalPort.supplier_id,
        ],
    )

    services = relationship(
        "SupplierService",
        lazy="noload",
        primaryjoin=lambda: and_(
            Supplier.code == SupplierService.supplier_code,
        ),
        foreign_keys=lambda: [
            SupplierService.supplier_code,
        ],
    )

    colors = relationship(
        "SupplierColor",
        lazy="noload",
        viewonly=True,
        primaryjoin=lambda: and_(
            Supplier.code == SupplierColor.supplier_id,
        ),
        foreign_keys=lambda: [
            SupplierColor.supplier_id,
        ],
    )

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "codpro"),
        {"schema": "PUB"},
    )


class SupplierService(PromecBase):
    __tablename__ = "opeservprov"

    supplier_code: Mapped[str] = mapped_column(
        "codpro", String(length=SUPPLIER_CODE_MAX_LENGTH)
    )
    service_code: Mapped[str] = mapped_column(
        "codser", String(length=SERVICE_CODE_MAX_LENGTH)
    )
    sequence_number: Mapped[int] = mapped_column("nrocorr")

    __table_args__ = (PrimaryKeyConstraint("codpro", "codser"), {"schema": "PUB"})


class Fiber(Base):
    __tablename__ = "fibras"

    id: Mapped[str] = mapped_column(
        String(length=FIBER_ID_MAX_LENGTH), primary_key=True
    )
    category_id: Mapped[int] = mapped_column("categoria_param_id")
    denomination: Mapped[str] = mapped_column(
        "denominacion", String(length=FIBER_DENOMINATION_MAX_LENGTH), nullable=True
    )
    origin: Mapped[str] = mapped_column(
        "procedencia", String(length=FIBER_ORIGIN_MAX_LENGTH), nullable=True
    )
    color_id: Mapped[str] = mapped_column(
        String(length=MECSA_COLOR_ID_MAX_LENGTH), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    category: Mapped[Parameter] = relationship(
        Parameter,
        lazy="noload",
        primaryjoin="Fiber.category_id == Parameter.id",
        foreign_keys="[Fiber.category_id]",
    )

    __table_args__ = (
        UniqueConstraint(
            "categoria_param_id",
            "denominacion",
            "procedencia",
            "color_id",
        ),
    )


class BaseUnit(PromecBase):
    __tablename__ = "AlmUnidades"

    code: Mapped[str] = mapped_column("CodUnd", primary_key=True)
    description: Mapped[str] = mapped_column("DesUnd")

    derived_units: Mapped[list["DerivedUnit"]] = relationship(
        "DerivedUnit",
        lazy="noload",
        primaryjoin="BaseUnit.code == foreign(DerivedUnit.base_code)",
    )

    __table_args__ = ({"schema": "PUB"},)


class DerivedUnit(PromecBase):
    __tablename__ = "almequiv"

    code: Mapped[str] = mapped_column("UndEqu", primary_key=True)
    base_code: Mapped[str] = mapped_column("CodUnd", primary_key=True)
    description: Mapped[str] = mapped_column("DesEqu")
    factor: Mapped[float] = mapped_column("Factor")
    sunat_code: Mapped[str] = mapped_column("UniMed_Sunat")

    __table_args__ = ({"schema": "PUB"},)


class InventoryItem(PromecBase):
    __tablename__ = "almprodg"

    company_code: Mapped[str] = mapped_column(
        "CodCia", primary_key=True, default=MECSA_COMPANY_CODE
    )
    id: Mapped[str] = mapped_column("CodProd", primary_key=True)
    family_id: Mapped[str] = mapped_column("CodFam")
    subfamily_id: Mapped[str] = mapped_column("SubFam", default="")
    base_unit_code: Mapped[str] = mapped_column("UndMed")
    inventory_unit_code: Mapped[str] = mapped_column("CodUnd")
    purchase_unit_code: Mapped[str] = mapped_column("UndCmp")
    is_active: Mapped[str] = mapped_column("Condicion", default=ACTIVE_STATUS_PROMEC)
    barcode: Mapped[int] = mapped_column("CodBarras", default=0)
    order_: Mapped[str] = mapped_column("Orden", default="A")

    description: Mapped[str] = mapped_column("DesProd")
    purchase_description_: Mapped[str] = mapped_column("DesCompra")
    purchase_description: Mapped[str] = column_property(
        func.substr(
            purchase_description_,
            literal_column("1"),
            literal_column(str(INVENTORY_ITEM_PURCHASE_DESCRIPTION_MAX_LENGTH)),
        )
    )

    field1: Mapped[str] = mapped_column("Estruct1", default="", nullable=True)
    field2: Mapped[str] = mapped_column("Estruct2", default="", nullable=True)
    field3: Mapped[str] = mapped_column("Estruct3", default="", nullable=True)
    field4: Mapped[str] = mapped_column("Estruct4", default="", nullable=True)
    field5: Mapped[str] = mapped_column("Estruct5", default="", nullable=True)

    yarn_color: Mapped[MecsaColor] = relationship(
        MecsaColor,
        lazy="noload",
        primaryjoin=lambda: and_(
            InventoryItem.field4 == MecsaColor.id,
        ),
        foreign_keys=lambda: [
            MecsaColor.id,
        ],
        viewonly=True,
    )

    fabric_color: Mapped[MecsaColor] = relationship(
        MecsaColor,
        lazy="noload",
        primaryjoin=lambda: and_(
            InventoryItem.field3 == MecsaColor.id,
        ),
        foreign_keys=lambda: [
            MecsaColor.id,
        ],
        viewonly=True,
    )

    fabric_recipe: Mapped[list["FabricYarn"]] = relationship(
        lazy="noload",
        primaryjoin=lambda: and_(
            InventoryItem.company_code == FabricYarn.company_code,
            InventoryItem.id == FabricYarn.fabric_id,
        ),
        foreign_keys=lambda: [
            FabricYarn.company_code,
            FabricYarn.fabric_id,
        ],
        viewonly=True, # This is required when assigning old recipes.
    )

    __table_args__ = ({"schema": "PUB"},)


class ProductInventory(PromecBase):
    __tablename__ = "almprodalm"

    company_code: Mapped[str] = mapped_column(
        "codcia", String(length=COMPANY_CODE_MAX_LENGTH)
    )
    period: Mapped[int] = mapped_column("periodo")
    storage_code: Mapped[str] = mapped_column(
        "codalm", String(length=STORAGE_CODE_MAX_LENGTH)
    )
    product_code: Mapped[str] = mapped_column(
        "codprod", String(length=PRODUCT_CODE_MAX_LENGTH)
    )
    current_stock: Mapped[float] = mapped_column("stkact")

    __table_args__ = (
        PrimaryKeyConstraint("codcia", "periodo", "codalm", "codprod"),
        {"schema": "PUB"},
    )

    def __repr__(self):
        return (
            f"<ProductInventory(\n"
            f"company_code={self.company_code},\n"
            f"period={self.period},\n"
            f"storage_code={self.storage_code},\n"
            f"product_code={self.product_code},\n"
            f"current_stock={self.current_stock}\n"
            f")>"
        )


class YarnFiber(Base):
    __tablename__ = "hilado_fibras"

    yarn_id: Mapped[str] = mapped_column(
        "hilado_id", String(length=YARN_ID_MAX_LENGTH), primary_key=True
    )
    fiber_id: Mapped[str] = mapped_column(
        "fibra_id", String(length=FIBER_ID_MAX_LENGTH), primary_key=True
    )
    proportion: Mapped[float] = mapped_column("proporcion", nullable=False)

    # fiber: Mapped[Fiber] = relationship()

    __table_args__ = (
        ForeignKeyConstraint(
            ["fibra_id"],
            ["fibras.id"],
        ),
    )


class Series(PromecBase):
    __tablename__ = "admseries"

    company_code: Mapped[str] = mapped_column(
        "CodCia", default=MECSA_COMPANY_CODE, primary_key=True
    )
    document_code: Mapped[str] = mapped_column("CodDoc", primary_key=True)
    service_number: Mapped[int] = mapped_column("NroSer", primary_key=True)
    number: Mapped[int] = mapped_column("NroDoc")

    __table_args__ = ({"schema": "PUB"},)


class CurrencyExchange(PromecBase):
    __tablename__ = "cbdtpocmb"

    exchange_date: Mapped[date] = mapped_column("fecha")
    buy_rate: Mapped[float] = mapped_column("compra")
    sell_rate: Mapped[float] = mapped_column("venta")

    __table_args__ = (
        PrimaryKeyConstraint("fecha"),
        {"schema": "PUB"},
    )


class FabricYarn(PromecBase):
    __tablename__ = "operectej"

    company_code: Mapped[str] = mapped_column(
        "CodCia", default=MECSA_COMPANY_CODE, primary_key=True
    )
    fabric_id: Mapped[str] = mapped_column("CodTej", primary_key=True)
    yarn_id: Mapped[str] = mapped_column("CodProd", primary_key=True)
    color_id: Mapped[str] = mapped_column("CodCol", primary_key=True, default="")
    proportion: Mapped[float] = mapped_column("PorHil")

    num_plies: Mapped[int] = mapped_column("nro_cabos", default=1)
    galgue: Mapped[float] = mapped_column("galga", default=0.0)
    diameter: Mapped[float] = mapped_column("diametro", default=0.0)
    stitch_length: Mapped[float] = mapped_column("longitud_malla", default=0.0)

    __table_args__ = ({"schema": "PUB"},)
