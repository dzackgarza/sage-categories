from collections.abc import Hashable as Hashable
from dataclasses import dataclass

from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.native import (
    NativeMorphismRealizations as NativeMorphismRealizations,
)
from sage_categories.cat.native import (
    NativeObjectRealizations as NativeObjectRealizations,
)
from sage_categories.sets.finite import SetsCategory as SetsCategory

__all__ = [
    "FiniteIndexing",
    "finite_native_morphism",
    "finite_native_object",
    "has_finite_native_morphism",
    "has_finite_native_object",
    "retain_finite_native_morphism",
    "retain_finite_native_object",
]

@dataclass(frozen=True, eq=False, slots=True)
class FiniteIndexing:
    data: tuple[Hashable, ...]

def retain_finite_native_object(value: SetsCategory.ObjectType, native: object, indexing: tuple[Hashable, ...]): ...
def finite_native_object(value: SetsCategory.ObjectType): ...
def has_finite_native_object(value: SetsCategory.ObjectType) -> bool: ...
def retain_finite_native_morphism(value: SetsCategory.MorphismType, native: object): ...
def finite_native_morphism(value: SetsCategory.MorphismType): ...
def has_finite_native_morphism(value: SetsCategory.MorphismType) -> bool: ...
