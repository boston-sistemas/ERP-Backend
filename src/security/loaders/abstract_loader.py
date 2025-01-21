from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.result import Failure
from src.security.failures import (
    PARAMETER_DISABLED_FAILURE,
    PARAMETER_NOT_FOUND_FAILURE,
)
from src.security.repositories import ParameterRepository


class AbstractParameterLoader(ABC):
    not_found_failure: Failure = PARAMETER_NOT_FOUND_FAILURE
    disabled_failure: Failure = PARAMETER_DISABLED_FAILURE

    def __init__(self, db: AsyncSession) -> None:
        self.repository = ParameterRepository(db=db)
