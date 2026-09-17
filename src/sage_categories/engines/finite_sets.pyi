from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import ConeCategory as ConeCategory
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.finite_categories import FiniteCategoryData as FiniteCategoryData
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Unknown as Unknown, UnknownClass as UnknownClass
from sage_categories.engines.gap import FINITE_SETS_PACKAGES as FINITE_SETS_PACKAGES, load_packages as load_packages
from sage_categories.kernel.retention import identity_positions as identity_positions
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict
from sage_categories.sets._finite_cap import finite_native_morphism as finite_native_morphism, finite_native_object as finite_native_object, has_finite_native_morphism as has_finite_native_morphism, has_finite_native_object as has_finite_native_object, retain_finite_native_morphism as retain_finite_native_morphism, retain_finite_native_object as retain_finite_native_object
from typing import Literal

def cartesian_associator(first: object, second: object, third: object, source: object, target: object, *, forward: bool) -> MorphismCategory.ObjectType:
    ...

def cartesian_left_unitor(value: object, source: object, target: object, *, forward: bool) -> MorphismCategory.ObjectType:
    ...

def cartesian_right_unitor(value: object, source: object, target: object, *, forward: bool) -> MorphismCategory.ObjectType:
    ...

def is_monomorphism(value: MorphismCategory.ObjectType) -> bool:
    ...

def is_epimorphism(value: MorphismCategory.ObjectType) -> bool:
    ...

def equal_morphisms(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> bool:
    ...

def inverse_morphism(value: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def image_factorization(value: MorphismCategory.ObjectType) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    ...

def factor_through_monomorphism(mono: MorphismCategory.ObjectType, value: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType | Literal[False]:
    ...

def hom_morphisms(source: object, target: object) -> tuple[MorphismCategory.ObjectType, ...]:
    ...

def finite_limit(diagram: Functor) -> object:
    ...

def finite_colimit(diagram: Functor) -> object:
    ...

def primitive_limit(diagram: Functor) -> object:
    ...

def primitive_colimit(diagram: Functor) -> object:
    ...
