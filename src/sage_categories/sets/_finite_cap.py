"""Owner-side reconstruction records for the private FinSetsForCAP realization."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass

from sage_categories.cat.native import (
    NativeMorphismRealizations,
    NativeObjectRealizations,
)
from sage_categories.sets.finite import Sets, SetsCategory

__all__ = [
    "FiniteIndexing",
    "finite_native_morphism",
    "finite_native_object",
    "retain_finite_native_morphism",
    "retain_finite_native_object",
]


@dataclass(frozen=True, eq=False, slots=True)
class FiniteIndexing:
    """The private skeletal indexing of one exact owned finite set."""

    data: tuple[Hashable, ...]


_objects: NativeObjectRealizations[object, FiniteIndexing] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[object] = NativeMorphismRealizations()


def retain_finite_native_object(
    value: SetsCategory.ObjectType,
    native: object,
    indexing: tuple[Hashable, ...],
):
    """Retain a native finite set without changing ``value``'s public enumeration."""
    assert len(indexing) == len(value), (
        f"private finite indexing has {len(indexing)} representatives for a set of size {len(value)}"
    )
    return _objects.retain(Sets, value, native, FiniteIndexing(indexing))


def finite_native_object(value: SetsCategory.ObjectType):
    return _objects.realization(value)


def retain_finite_native_morphism(value: SetsCategory.MorphismType, native: object):
    return _morphisms.retain(Sets, value, value.domain(), value.codomain(), native)


def finite_native_morphism(value: SetsCategory.MorphismType):
    return _morphisms.realization(value)
