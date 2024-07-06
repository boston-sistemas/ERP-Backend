from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


class Result(Generic[T, E]):
    def __init__(self, value: T | None = None, error: E | None = None):
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._error is None

    @property
    def is_failure(self) -> bool:
        return self._error is not None

    @property
    def value(self) -> T:
        if self.is_failure:
            raise ValueError("No value, this is a failure result")
        return self._value

    @property
    def error(self) -> E:
        if self.is_success:
            raise ValueError("No error, this is a success result")
        return self._error


class Success(Result):
    def __init__(self, value: T):
        super().__init__(value=value)


class Failure(Result):
    def __init__(self, error: E):
        super().__init__(error=error)
