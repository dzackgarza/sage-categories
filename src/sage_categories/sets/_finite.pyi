from collections.abc import Hashable, Iterable

def cartesian(factors: Iterable[tuple[Hashable, ...]]) -> tuple[tuple[Hashable, ...], ...]:
    ...

def quotient(values: tuple[Hashable, ...], pairs: Iterable[tuple[Hashable, Hashable]]) -> dict[Hashable, frozenset[Hashable]]:
    ...
