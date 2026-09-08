"""Finite functor-category structural computation through GAP FunctorCategories."""

from __future__ import annotations

from sage.libs.gap.libgap import libgap

from sage_categories.cat.functors import Cat
from sage_categories.cat.morphisms import Mor
from sage_categories.engines import fp_categories
from sage_categories.engines.gap import FUNCTOR_CATEGORIES, load_repository_package

__all__ = ["arrow_category"]

_loaded = False


def _load() -> None:
    global _loaded
    if not _loaded:
        load_repository_package(FUNCTOR_CATEGORIES)
        _loaded = True


def arrow_category(category: object, target: object, arrows: tuple[object, ...]):
    """Exact finite data for ``Fun([1], target)`` with native naturality checks."""
    _load()
    interval = Cat().Simplex(1)
    native = libgap.FunctorCategory(
        fp_categories.native_category(interval),
        fp_categories.native_category(target),
    )
    native_objects: dict[int, object] = {}
    for arrow in arrows:
        native_objects[id(arrow)] = libgap.AsObjectInFunctorCategoryByValues(
            native,
            [
                fp_categories.native_object(target, arrow.domain()),
                fp_categories.native_object(target, arrow.codomain()),
            ],
            [fp_categories.native_morphism(target, arrow)],
        )
    morphisms = []
    zero = interval(0)
    for source in arrows:
        for destination in arrows:
            transformations = libgap.MorphismsOfExternalHom(
                native,
                native_objects[id(source)],
                native_objects[id(destination)],
            )
            for transformation in transformations:
                components = tuple(
                    fp_categories.owned_morphism(target, component)
                    for component in libgap.ValuesOnAllObjects(transformation)
                )
                assert len(components) == 2
                morphisms.append(
                    Mor(category)(source, destination)(
                        lambda vertex, components=components: (
                            components[0] if vertex is zero else components[1]
                        )
                    )
                )
    return tuple(arrows), tuple(morphisms)
