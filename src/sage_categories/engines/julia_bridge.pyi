from dataclasses import dataclass
from functools import cache
from typing import Any
from _typeshed import Incomplete

@cache
def catlab_bridge() -> Any:
    ...

@dataclass(frozen=True, eq=False, slots=True)
class OscarHandle:
    index: int

class _OscarBridge:

    def __init__(self) -> None:
        ...

    def handle(self, operation: str, *arguments: object) -> OscarHandle:
        ...

    def pair(self, operation: str, *arguments: object) -> tuple[OscarHandle, OscarHandle]:
        ...

    def handle_and_handles(self, operation: str, *arguments: object) -> tuple[OscarHandle, tuple[OscarHandle, ...]]:
        ...

    def handles(self, operation: str, *arguments: object) -> tuple[OscarHandle, ...]:
        ...

    def boolean(self, operation: str, *arguments: object) -> bool:
        ...

    def text(self, operation: str, *arguments: object) -> str:
        ...

@cache
def oscar_bridge() -> _OscarBridge:
    ...

class _OscarWorker:
    _stderr_path: Incomplete
    _stderr: Incomplete
    _process: Incomplete
    _stdin: Incomplete
    _stdout: Incomplete
    _lock: Incomplete

    def __init__(self) -> None:
        ...

    def close(self) -> None:
        ...

    def request(self, operation: str, *arguments: object) -> object:
        ...
