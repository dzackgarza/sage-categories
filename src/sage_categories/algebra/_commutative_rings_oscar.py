"""Owner-side reconstruction records for OSCAR realizations of commutative rings."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealization,
    NativeMorphismRealizations,
    NativeObjectRealization,
    NativeObjectRealizations,
)

__all__ = [
    "OscarRingConstruction",
    "oscar_native_morphism",
    "oscar_native_object",
    "retain_oscar_native_morphism",
    "retain_oscar_native_object",
]


@dataclass(frozen=True, eq=False, slots=True)
class OscarRingConstruction:
    """The owned construction data selecting one OSCAR commutative-ring realization."""

    data: object


_objects: NativeObjectRealizations[object, OscarRingConstruction] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[object] = NativeMorphismRealizations()


def _owner() -> Any:
    structured_objects = import_module("sage_categories.cat.structured_objects")
    declarations = import_module("sage_categories.cat.declarations")
    return structured_objects.Rings(declarations.Sets).Commutative()


def retain_oscar_native_object(
    value: CategoryOfCategories.ElementType,
    native: object,
    construction: object,
) -> NativeObjectRealization[object, OscarRingConstruction]:
    """Retain one native ring against its exact owned commutative-ring object."""
    return _objects.retain(_owner(), value, native, OscarRingConstruction(construction))


def oscar_native_object(
    value: CategoryOfCategories.ElementType,
) -> NativeObjectRealization[object, OscarRingConstruction]:
    return _objects.realization(value)


def retain_oscar_native_morphism(
    value: MorphismCategory.ObjectType, native: object
) -> NativeMorphismRealization[object]:
    """Retain one native ring map with the exact owned source and target rings."""
    return _morphisms.retain(_owner(), value, value.domain(), value.codomain(), native)


def oscar_native_morphism(
    value: MorphismCategory.ObjectType,
) -> NativeMorphismRealization[object]:
    return _morphisms.realization(value)
