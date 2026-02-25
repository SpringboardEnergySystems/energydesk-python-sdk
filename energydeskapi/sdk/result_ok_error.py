from dataclasses import dataclass
from typing import TypeVar, Generic, Union

T = TypeVar("T")  # The type of the success value
E = TypeVar("E")  # The type of the error message/exception

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

    @property
    def is_ok(self) -> bool:
        return True

@dataclass(frozen=True)
class Error(Generic[E]):
    error: E

    @property
    def is_ok(self) -> bool:
        return False

# A type alias for easier usage
Result = Union[Ok[T], Error[E]]

