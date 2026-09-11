from collections.abc import Hashable
from dataclasses import dataclass
from sage_categories.sets.finite import SetsCategory
__all__ = ['FiniteIndexing', 'retain_finite_native_object', 'finite_native_object', 'retain_finite_native_morphism', 'finite_native_morphism']

@dataclass(frozen=True, eq=False, slots=True)
class FiniteIndexing:
    data: tuple[Hashable, ...]

def retain_finite_native_object(value: SetsCategory.ObjectType, native: object, indexing: tuple[Hashable, ...]):
    ...

def finite_native_object(value: SetsCategory.ObjectType):
    ...

def retain_finite_native_morphism(value: SetsCategory.MorphismType, native: object):
    ...

def finite_native_morphism(value: SetsCategory.MorphismType):
    ...
