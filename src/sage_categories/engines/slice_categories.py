"""Finite slice structural computation through GAP SliceCategories."""

from __future__ import annotations

from sage.libs.gap.libgap import libgap

from sage_categories.engines import fp_categories
from sage_categories.engines.gap import SLICE_CATEGORIES, load_repository_package

__all__ = ["slice_category"]

_loaded = False


def _load() -> None:
    global _loaded
    if not _loaded:
        load_repository_package(SLICE_CATEGORIES)
        _loaded = True


def slice_category(category: object, base: object, arrows: tuple[object, ...]):
    """Exact finite data for ``base.SliceOver(x)`` using native slice Hom sets."""
    _load()
    assert category._fixed_label == 1, "native slice execution currently models SliceOver"
    fixed = category.fixed_object()
    native_slice = libgap.SliceCategory(fp_categories.native_object(base, fixed))

    owned_objects: list[object] = []
    native_objects: dict[int, object] = {}
    for arrow in arrows:
        if arrow.codomain() is not fixed:
            continue
        owned = category(arrow)
        owned_objects.append(owned)
        native_objects[id(owned)] = libgap.AsSliceCategoryCell(
            fp_categories.native_morphism(base, arrow),
            native_slice,
        )

    owned_morphisms: list[object] = []
    for source in owned_objects:
        for target in owned_objects:
            native_source = native_objects[id(source)]
            native_target = native_objects[id(target)]
            for native in libgap.MorphismsOfExternalHom(native_source, native_target):
                varying = fp_categories.owned_morphism(base, libgap.UnderlyingCell(native))
                owned_morphisms.append(category.construct_morphism(source, target, varying))
    return tuple(owned_objects), tuple(owned_morphisms)
