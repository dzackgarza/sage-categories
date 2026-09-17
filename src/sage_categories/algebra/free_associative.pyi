from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from sage_categories.algebra.abelian import AbelianBimoduleTensor as AbelianBimoduleTensor, AbelianTensor as AbelianTensor, balanced_tensor as balanced_tensor, indexed_free_abelian_injection as indexed_free_abelian_injection, relative_tensor as relative_tensor, relative_tensor_mediator as relative_tensor_mediator
from sage_categories.algebra.indexed_modules import indexed_free_integer_coefficients as indexed_free_integer_coefficients, indexed_free_integer_element as indexed_free_integer_element, indexed_free_integer_homomorphism as indexed_free_integer_homomorphism, indexed_free_integer_module as indexed_free_integer_module, integer_scalar_monoid as integer_scalar_monoid
from sage_categories.cat.bimodules import Bimodules as Bimodules
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.modules import ModuleCategory as ModuleCategory
from sage_categories.cat.monoidal import MonoidalStructuresCategory as MonoidalStructuresCategory, tensor_object as tensor_object
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.native import NativeObjectRealizations as NativeObjectRealizations
from sage_categories.cat.structured_objects import Magmas as Magmas, MonoidCategory as MonoidCategory, Monoids as Monoids
from sage_categories.engines import free_algebras as free_algebras
from sage_categories.sets.finite import Sets as Sets
type Word = tuple[int, ...]

@dataclass(frozen=True, eq=False, slots=True)
class IntegerFreeAssociativeConstruction:
    names: tuple[str, ...]
    word_module: CategoryOfCategories.ElementType

def integer_free_associative_algebra(names: Sequence[str]=('x', 'y')) -> MonoidCategory.ObjectType:
    ...

def free_associative_underlying_module(algebra: MonoidCategory.ObjectType) -> ModuleCategory.ObjectType:
    ...

def free_associative_element(algebra: MonoidCategory.ObjectType, terms: Mapping[Word, int]) -> ModuleCategory.ElementType:
    ...

def free_associative_generator(algebra: MonoidCategory.ObjectType, position: int) -> ModuleCategory.ElementType:
    ...

def free_associative_coefficients(algebra: MonoidCategory.ObjectType, element: ModuleCategory.ElementType) -> dict[Word, int]:
    ...

def free_associative_product(algebra: MonoidCategory.ObjectType, left: ModuleCategory.ElementType, right: ModuleCategory.ElementType) -> ModuleCategory.ElementType:
    ...

def free_associative_substitution(algebra: MonoidCategory.ObjectType, images: Sequence[ModuleCategory.ElementType]) -> MorphismCategory.ObjectType:
    ...

def free_associative_underlying_morphism(algebra_morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...
