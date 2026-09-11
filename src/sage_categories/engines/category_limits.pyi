from collections.abc import Callable

from sage_categories.engines.gap import FINITE_SETS_PACKAGES as FINITE_SETS_PACKAGES
from sage_categories.engines.gap import load_packages as load_packages

__all__ = ["compatible_families", "identified_objects", "matching_triples"]

def compatible_families(
    vertices: tuple[object, ...],
    arrows: tuple[object, ...],
    families: tuple[tuple[object, ...], ...],
    image: Callable[[object, object], object],
    locate: Callable[[tuple[object, ...], object], int],
) -> tuple[tuple[object, ...], ...]: ...
def identified_objects(
    vertices: tuple[object, ...],
    arrows: tuple[object, ...],
    families: tuple[tuple[object, ...], ...],
    image: Callable[[object, object], object],
    locate: Callable[[tuple[object, ...], object], int],
) -> tuple[int, tuple[tuple[int, ...], ...]]: ...
def matching_triples(
    source_values: tuple[object, ...],
    target_values: tuple[object, ...],
    morphisms: tuple[object, ...],
    reindex: Callable[[object], object],
    domain: Callable[[object], object],
    codomain: Callable[[object], object],
    locate: Callable[[tuple[object, ...], object], int],
) -> tuple[tuple[object, object, object], ...]: ...
