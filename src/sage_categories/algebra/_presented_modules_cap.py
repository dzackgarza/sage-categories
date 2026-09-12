"""Owner-side reconstruction records for native presentations of objects of ``Ab``."""

from __future__ import annotations

from dataclasses import dataclass

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealizations,
    NativeObjectRealizations,
)

__all__ = [
    "PresentedModuleConstruction",
    "has_presented_native_morphism",
    "has_presented_native_object",
    "presented_native_morphism",
    "presented_native_object",
    "retain_presented_native_morphism",
    "retain_presented_native_object",
]


@dataclass(frozen=True, eq=False, slots=True)
class PresentedModuleConstruction:
    """The owned presentation data selecting this native module realization."""

    data: object


_objects: NativeObjectRealizations[object, PresentedModuleConstruction] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[object] = NativeMorphismRealizations()


def has_presented_native_object(value: CategoryOfCategories.ElementType) -> bool:
    """Whether ``value`` already retains a native presented-module realization."""
    return _objects.has(value)


def has_presented_native_morphism(value: MorphismCategory.ObjectType) -> bool:
    """Whether ``value`` already retains a native presented-module morphism."""
    return _morphisms.has(value)


def retain_presented_native_object(
    value: CategoryOfCategories.ElementType,
    native: object,
    construction: object,
):
    from sage_categories.algebra.abelian import AbelianGroups

    return _objects.retain(AbelianGroups(), value, native, PresentedModuleConstruction(construction))


def presented_native_object(value: CategoryOfCategories.ElementType):
    return _objects.realization(value)


def retain_presented_native_morphism(value: MorphismCategory.ObjectType, native: object):
    from sage_categories.algebra.abelian import AbelianGroups

    return _morphisms.retain(AbelianGroups(), value, value.domain(), value.codomain(), native)


def presented_native_morphism(value: MorphismCategory.ObjectType):
    return _morphisms.realization(value)
