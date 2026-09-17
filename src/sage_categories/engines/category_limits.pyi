from collections.abc import Callable
from sage.libs.gap.element import GapElement as GapElement
from sage_categories.engines.gap import FINITE_SETS_PACKAGES as FINITE_SETS_PACKAGES, load_packages as load_packages
from sage_categories.kernel.retention import identity_positions as identity_positions

def compatible_families(vertices: tuple[object, ...], arrows: tuple[object, ...], families: tuple[tuple[object, ...], ...], image: Callable[[object, object], object], locate: Callable[[tuple[object, ...], object], int]) -> tuple[tuple[object, ...], ...]:
    ...

def identified_objects(vertices: tuple[object, ...], arrows: tuple[object, ...], families: tuple[tuple[object, ...], ...], image: Callable[[object, object], object], locate: Callable[[tuple[object, ...], object], int]) -> tuple[int, tuple[tuple[int, ...], ...]]:
    ...

def matching_triples(source_values: tuple[object, ...], target_values: tuple[object, ...], morphisms: tuple[object, ...], reindex: Callable[[object], object], domain: Callable[[object], object], codomain: Callable[[object], object], locate: Callable[[tuple[object, ...], object], int]) -> tuple[tuple[object, object, object], ...]:
    ...
