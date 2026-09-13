"""Finite slice structural computation through GAP SliceCategories."""

from __future__ import annotations

from sage.libs.gap.libgap import libgap

from sage_categories.engines import fp_categories
from sage_categories.engines.gap import SLICE_CATEGORIES, load_repository_package
from sage_categories.kernel.sage_runtime import MonoDict

__all__ = ["slice_category"]


def slice_category(category: object, base: object, arrows: tuple[object, ...]):
    """Exact finite data for ``base.SliceOver(x)`` using native slice Hom sets."""
    load_repository_package(SLICE_CATEGORIES)
    fixed = category.fixed_object()
    native_slice = libgap.SliceCategory(fp_categories.native_object(base, fixed))

    owned_objects: list[object] = []
    native_objects: MonoDict = MonoDict()
    for arrow in arrows:
        if arrow.codomain() is not fixed:
            continue
        owned = category(arrow)
        owned_objects.append(owned)
        native_objects[owned] = libgap.AsSliceCategoryCell(
            fp_categories.native_morphism(base, arrow),
            native_slice,
        )

    owned_morphisms: list[object] = []
    for source in owned_objects:
        for target in owned_objects:
            native_source = native_objects[source]
            native_target = native_objects[target]
            for native in libgap.MorphismsOfExternalHom(native_source, native_target):
                varying = fp_categories.owned_morphism(base, libgap.UnderlyingCell(native))
                owned_morphisms.append(category.construct_morphism(source, target, varying))
    return tuple(owned_objects), tuple(owned_morphisms)
