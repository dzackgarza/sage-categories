from typing import Literal

from sage_categories.cat.cones import ConeCategory as ConeCategory
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.engines.gap import FINITE_SETS_PACKAGES as FINITE_SETS_PACKAGES
from sage_categories.engines.gap import load_packages as load_packages
from sage_categories.sets._finite_cap import (
    finite_native_morphism as finite_native_morphism,
)
from sage_categories.sets._finite_cap import (
    finite_native_object as finite_native_object,
)
from sage_categories.sets._finite_cap import (
    retain_finite_native_morphism as retain_finite_native_morphism,
)
from sage_categories.sets._finite_cap import (
    retain_finite_native_object as retain_finite_native_object,
)

__all__ = [
    "cartesian_associator",
    "cartesian_left_unitor",
    "cartesian_right_unitor",
    "equal_morphisms",
    "factor_through_monomorphism",
    "finite_colimit",
    "finite_limit",
    "hom_morphisms",
    "image_factorization",
    "inverse_morphism",
    "is_epimorphism",
    "is_monomorphism",
    "primitive_colimit",
    "primitive_limit",
]

def cartesian_associator(first: object, second: object, third: object, source: object, target: object, *, forward: bool) -> MorphismCategory.ObjectType: ...
def cartesian_left_unitor(value: object, source: object, target: object, *, forward: bool) -> MorphismCategory.ObjectType: ...
def cartesian_right_unitor(value: object, source: object, target: object, *, forward: bool) -> MorphismCategory.ObjectType: ...
def is_monomorphism(value: MorphismCategory.ObjectType) -> bool: ...
def is_epimorphism(value: MorphismCategory.ObjectType) -> bool: ...
def equal_morphisms(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> bool: ...
def inverse_morphism(value: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType: ...
def image_factorization(value: MorphismCategory.ObjectType) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]: ...
def factor_through_monomorphism(mono: MorphismCategory.ObjectType, value: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType | Literal[False]: ...
def hom_morphisms(source: object, target: object) -> tuple[MorphismCategory.ObjectType, ...]: ...
def finite_limit(diagram: Functor) -> object: ...
def finite_colimit(diagram: Functor) -> object: ...
def primitive_limit(diagram: Functor) -> object: ...
def primitive_colimit(diagram: Functor) -> object: ...
