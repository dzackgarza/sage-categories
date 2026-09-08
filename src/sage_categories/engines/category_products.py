"""Finite products of presented categories through CAP's category product."""

from __future__ import annotations

from sage.libs.gap.element import GapElement
from sage.libs.gap.libgap import libgap

from sage_categories.engines import fp_categories
from sage_categories.engines.gap import FINITE_CATEGORY_PACKAGES, load_packages

__all__ = ["finite_product_data"]

_loaded = False


def _load() -> None:
    global _loaded
    if not _loaded:
        load_packages(FINITE_CATEGORY_PACKAGES)
        _loaded = True


def _cartesian(families: tuple[tuple[GapElement, ...], ...]) -> tuple[tuple[GapElement, ...], ...]:
    if not families:
        return ((),)
    return tuple(tuple(values) for values in libgap.Cartesian(*families))


def finite_product_data(
    factors: tuple[object, ...],
    object_families: tuple[tuple[object, ...], ...],
    morphism_families: tuple[tuple[object, ...], ...],
) -> tuple[tuple[tuple[object, ...], ...], tuple[tuple[object, ...], ...]]:
    """Return exact component families for a finite product, computed by CAP/GAP.

    CAP owns the product category and product cells.  The returned tuples are the
    owned components reconstructed from those native product cells.
    """
    _load()
    native_factors = tuple(fp_categories.native_category(factor) for factor in factors)
    product_category = libgap.ProductCategory(list(native_factors))

    native_objects = tuple(
        tuple(fp_categories.native_object(factor, value) for value in family)
        for factor, family in zip(factors, object_families, strict=True)
    )
    objects: list[tuple[object, ...]] = []
    for components in _cartesian(native_objects):
        product_object = libgap.ProductCategoryObject(product_category, list(components))
        objects.append(
            tuple(
                fp_categories.owned_object(factor, component)
                for factor, component in zip(factors, libgap.Components(product_object), strict=True)
            )
        )

    native_morphisms = tuple(
        tuple(fp_categories.native_morphism(factor, value) for value in family)
        for factor, family in zip(factors, morphism_families, strict=True)
    )
    morphisms: list[tuple[object, ...]] = []
    for components in _cartesian(native_morphisms):
        product_morphism = libgap.ProductCategoryMorphism(product_category, list(components))
        morphisms.append(
            tuple(
                fp_categories.owned_morphism(factor, component)
                for factor, component in zip(factors, libgap.Components(product_morphism), strict=True)
            )
        )
    return tuple(objects), tuple(morphisms)
