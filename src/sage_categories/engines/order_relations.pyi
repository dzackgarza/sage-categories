from collections.abc import Hashable as Hashable

def is_partial_order(elements: tuple[Hashable, ...], relation: frozenset[tuple[Hashable, Hashable]]) -> bool:
    ...

def is_total_order(elements: tuple[Hashable, ...], relation: frozenset[tuple[Hashable, Hashable]]) -> bool:
    ...
