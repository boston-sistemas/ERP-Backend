from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import SERIES_NOT_FOUND_FAILURE
from src.operations.models import Series
from src.operations.repositories import SeriesRepository


class SeriesService:
    def __init__(self, promec_db: AsyncSession):
        self.repository = SeriesRepository(db=promec_db)

    async def read_series(
        self, document_code: str, service_number: int
    ) -> Result[Series, CustomException]:
        series = await self.repository.find_series_by_id(
            document_code=document_code, service_number=service_number
        )

        if series is not None:
            return Success(series)

        return SERIES_NOT_FOUND_FAILURE()

    async def next_number(
        self, document_code: str, service_number: int
    ) -> Result[int, CustomException]:
        result = await self.read_series(
            document_code=document_code, service_number=service_number
        )

        if result.is_failure:
            return result

        series: Series = result.value
        number = series.number
        series.number += 1
        await self.repository.save(series)

        return Success(number)


class SeriesHelper(SeriesService):
    name: str = ""
    document_code: str
    service_number: int

    def __init_subclass__(
        cls,
        name: str = "",
        document_code: str = None,
        service_number: int = None,
        **kwargs,
    ):
        if document_code is None:
            raise TypeError(f"{cls.__name__} requires 'document_code' to be defined.")
        if service_number is None:
            raise TypeError(f"{cls.__name__} requires 'service_number' to be defined.")
        cls.name = name
        cls.document_code = document_code
        cls.service_number = service_number
        super().__init_subclass__(**kwargs)

    def __init__(self, promec_db: AsyncSession):
        super().__init__(promec_db=promec_db)

    async def next_number(self) -> int:
        result = await super().next_number(
            document_code=self.document_code, service_number=self.service_number
        )
        if result.is_success:
            return result.value

        raise SERIES_NOT_FOUND_FAILURE(series_name=self.name)


class BarcodeSeries(
    SeriesHelper, name="Código de Barras", document_code="BAR", service_number=1
):
    pass


class MovementSeries(SeriesHelper, document_code="", service_number=0):
    async def next_number(self) -> str:
        result = await super().next_number()

        return str(self.service_number).zfill(3) + str(result).zfill(7)


class EntrySeries(
    MovementSeries,
    name="Ingreso a almacén proveedor",
    document_code="P/I",
    service_number=1,
):
    pass


class DispatchSeries(
    MovementSeries,
    name="Salida a tejeduría",
    document_code="P/S",
    service_number=1,
):
    pass


class YarnPurchaseEntrySeries(
    MovementSeries,
    name="Ingreso por compra de hilado",
    document_code="P/I",
    service_number=6,
):
    pass


class YarnWeavingDispatchSeries(
    MovementSeries,
    name="Salida de hilado a tejeduría",
    document_code="G/R",
    service_number=104,
):
    async def next_number(self) -> str:
        result = await super().next_number()

        return "T" + result


class DyeingServiceDispatchSeries(
    MovementSeries,
    name="Salida de tejido a tintorería",
    document_code="G/R",
    service_number=104,
):
    async def next_number(self) -> str:
        result = await super().next_number()

        return "T" + result


class WeavingServiceEntrySeries(
    MovementSeries,
    name="Ingreso de tejido por servicio de tejeduría",
    document_code="P/I",
    service_number=1,
):
    pass
