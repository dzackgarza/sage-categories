from collections.abc import Hashable

from sage_categories.cat.native import (
    NativeMorphismRealization,
    NativeObjectRealization,
)
from sage_categories.sets.finite import SetsCategory

class FiniteIndexing:
    data: tuple[Hashable, ...]

def retain_finite_native_object(value: SetsCategory.ObjectType, native: object, indexing: tuple[Hashable, ...]) -> NativeObjectRealization[object, FiniteIndexing]: ...
def finite_native_object(value: SetsCategory.ObjectType) -> NativeObjectRealization[object, FiniteIndexing]: ...
def retain_finite_native_morphism(value: SetsCategory.MorphismType, native: object) -> NativeMorphismRealization[object]: ...
def finite_native_morphism(value: SetsCategory.MorphismType) -> NativeMorphismRealization[object]: ...
