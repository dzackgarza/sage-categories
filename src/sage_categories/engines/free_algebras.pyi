from collections.abc import Mapping, Sequence
__all__ = ['integer_free_algebra', 'coefficients', 'multiply', 'substitute', 'generator', 'one']
type Word = tuple[int, ...]
type Terms = Mapping[Word, int]

def integer_free_algebra(names: Sequence[str]):
    ...

def coefficients(algebra, element) -> dict[Word, int]:
    ...

def multiply(algebra, left: Terms, right: Terms) -> dict[Word, int]:
    ...

def substitute(algebra, element: Terms, images: Sequence[Terms]) -> dict[Word, int]:
    ...

def generator(algebra, position: int) -> dict[Word, int]:
    ...

def one(algebra) -> dict[Word, int]:
    ...
