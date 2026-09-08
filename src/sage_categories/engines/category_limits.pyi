from collections.abc import Callable
from typing import Any

def compatible_families(
    vertices: tuple[Any, ...],
    arrows: tuple[Any, ...],
    families: tuple[tuple[Any, ...], ...],
    image: Callable[[Any, Any], Any],
    locate: Callable[[tuple[Any, ...], Any], int],
) -> tuple[tuple[Any, ...], ...]: ...


def matching_triples(
    source_values: tuple[object, ...],
    target_values: tuple[object, ...],
    morphisms: tuple[object, ...],
    reindex: Callable[[object], object],
    domain: Callable[[object], object],
    codomain: Callable[[object], object],
    locate: Callable[[tuple[object, ...], object], int],
) -> tuple[tuple[object, object, object], ...]: ...
def identified_objects(
    vertices: tuple[object, ...],
    arrows: tuple[object, ...],
    families: tuple[tuple[object, ...], ...],
    image: Callable[[object, object], object],
    locate: Callable[[tuple[object, ...], object], int],
) -> tuple[int, tuple[tuple[int, ...], ...]]: ...
