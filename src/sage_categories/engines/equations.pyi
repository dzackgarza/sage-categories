from typing import Any
__all__ = ['reduced_word', 'equal_morphisms']

class _Worker:

    def __init__(self) -> None:
        ...

    def request(self, operation: str, **payload: object) -> object:
        ...

class _Encoding:

    def __init__(self) -> None:
        ...

    def expression(self, morphism: object) -> list[Any]:
        ...

    def factors(self, indices: object) -> tuple[object, ...]:
        ...

def reduced_word(morphism: object) -> tuple[object, ...]:
    ...

def equal_morphisms(first: object, second: object) -> bool:
    ...
