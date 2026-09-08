"""FinSetsForCAP execution for finite owned sets and maps.

Owned labels and chosen enumerations remain in ``Sets``.  This module lowers one
finite owned presentation to ``SkeletalFinSets`` through the retained private
bijection and delegates finite-map algorithms to CAP.
"""

from __future__ import annotations

from functools import cache
from typing import Literal

from sage.libs.gap.element import GapElement
from sage.libs.gap.libgap import libgap

from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.engines.gap import FINITE_SETS_PACKAGES, load_packages
from sage_categories.sets._finite_cap import (
    finite_native_morphism,
    finite_native_object,
    retain_finite_native_morphism,
    retain_finite_native_object,
)

__all__ = [
    "equal_morphisms",
    "factor_through_monomorphism",
    "hom_morphisms",
    "image_factorization",
    "inverse_morphism",
    "is_epimorphism",
    "is_monomorphism",
]


@cache
def _category() -> GapElement:
    load_packages(FINITE_SETS_PACKAGES)
    return libgap.SkeletalFinSets


def _has_native_object(value: object) -> bool:
    try:
        finite_native_object(value)
    except AssertionError:
        return False
    return True


def _has_native_morphism(value: object) -> bool:
    try:
        finite_native_morphism(value)
    except AssertionError:
        return False
    return True


def _index(realization: object, datum: object) -> int:
    indexing = realization.construction.data
    owner = realization.value
    representative = owner.representative(datum)
    for index, candidate in enumerate(indexing):
        if owner.representative(candidate) == representative:
            return index
    raise AssertionError(f"{datum!r} has no private finite index in {owner!r}")


def _native_object(value: object) -> GapElement:
    if _has_native_object(value):
        return finite_native_object(value).native
    indexing = tuple(value._values)
    category = _category()
    native = libgap.FinSet(category, len(indexing))
    retain_finite_native_object(value, native, indexing)
    return native


def _native_morphism(value: MorphismCategory.ObjectType) -> GapElement:
    if _has_native_morphism(value):
        return finite_native_morphism(value).native
    source_record = finite_native_object(value.domain()) if _has_native_object(value.domain()) else None
    target_record = finite_native_object(value.codomain()) if _has_native_object(value.codomain()) else None
    source_native = _native_object(value.domain())
    target_native = _native_object(value.codomain())
    source_record = finite_native_object(value.domain()) if source_record is None else source_record
    target_record = finite_native_object(value.codomain()) if target_record is None else target_record
    graph = [
        _index(target_record, value._action(datum))
        for datum in source_record.construction.data
    ]
    native = libgap.MapOfFinSets(source_native, graph, target_native)
    retain_finite_native_morphism(value, native)
    return native


def _graph(native: GapElement) -> tuple[int, ...]:
    return tuple(int(index) for index in libgap.AsList(native))


def _owned_morphism(
    source: object,
    target: object,
    native: GapElement,
) -> MorphismCategory.ObjectType:
    from sage_categories.sets.finite import Sets

    source_record = finite_native_object(source)
    target_record = finite_native_object(target)
    graph = _graph(native)
    table = {
        datum: target_record.construction.data[graph[index]]
        for index, datum in enumerate(source_record.construction.data)
    }
    owned = Sets.MorphismType(
        domain=source,
        codomain=target,
        data=lambda datum: table[source.representative(datum)],
    )
    retain_finite_native_morphism(owned, native)
    return owned


def is_monomorphism(value: MorphismCategory.ObjectType) -> bool:
    return bool(libgap.IsMonomorphism(_native_morphism(value)))


def is_epimorphism(value: MorphismCategory.ObjectType) -> bool:
    return bool(libgap.IsEpimorphism(_native_morphism(value)))


def equal_morphisms(
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> bool:
    return bool(libgap.IsEqualForMorphisms(_native_morphism(first), _native_morphism(second)))


def inverse_morphism(value: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    native = _native_morphism(value)
    assert bool(libgap.IsIsomorphism(native)), f"{value!r} is not invertible"
    return _owned_morphism(value.codomain(), value.domain(), libgap.InverseForMorphisms(native))


def image_factorization(
    value: MorphismCategory.ObjectType,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    from sage_categories.sets.finite import Sets

    native = _native_morphism(value)
    computed_inclusion = libgap.ImageEmbedding(native)
    target_record = finite_native_object(value.codomain())
    image_indices = _graph(computed_inclusion)
    image_data = tuple(target_record.construction.data[index] for index in image_indices)
    image = Sets(image_data)
    native_image = _native_object(image)
    native_inclusion = libgap.MapOfFinSets(
        native_image, image_indices, _native_object(value.codomain())
    )
    computed_factor = libgap.CoastrictionToImage(native)
    native_factor = libgap.MapOfFinSets(
        _native_object(value.domain()), _graph(computed_factor), native_image
    )
    inclusion = _owned_morphism(image, value.codomain(), native_inclusion)
    factor = _owned_morphism(value.domain(), image, native_factor)
    return factor, inclusion


def factor_through_monomorphism(
    mono: MorphismCategory.ObjectType,
    value: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType | Literal[False]:
    native_value, native_mono = _native_morphism(value), _native_morphism(mono)
    if not bool(libgap.IsLiftable(native_value, native_mono)):
        return False
    return _owned_morphism(value.domain(), mono.domain(), libgap.Lift(native_value, native_mono))


def hom_morphisms(
    source: object,
    target: object,
) -> tuple[MorphismCategory.ObjectType, ...]:
    native_source, native_target = _native_object(source), _native_object(target)
    return tuple(
        _owned_morphism(source, target, native)
        for native in libgap.MorphismsOfExternalHom(native_source, native_target)
    )
