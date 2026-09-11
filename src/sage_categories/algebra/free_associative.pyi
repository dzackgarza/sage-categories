from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from sage_categories.algebra.abelian import (
    AbelianBimoduleTensor as AbelianBimoduleTensor,
)
from sage_categories.algebra.abelian import (
    AbelianTensor as AbelianTensor,
)
from sage_categories.algebra.abelian import (
    balanced_tensor as balanced_tensor,
)
from sage_categories.algebra.abelian import (
    indexed_free_abelian_injection as indexed_free_abelian_injection,
)
from sage_categories.algebra.abelian import (
    relative_tensor as relative_tensor,
)
from sage_categories.algebra.abelian import (
    relative_tensor_mediator as relative_tensor_mediator,
)
from sage_categories.algebra.indexed_modules import (
    indexed_free_integer_coefficients as indexed_free_integer_coefficients,
)
from sage_categories.algebra.indexed_modules import (
    indexed_free_integer_element as indexed_free_integer_element,
)
from sage_categories.algebra.indexed_modules import (
    indexed_free_integer_homomorphism as indexed_free_integer_homomorphism,
)
from sage_categories.algebra.indexed_modules import (
    indexed_free_integer_module as indexed_free_integer_module,
)
from sage_categories.algebra.indexed_modules import (
    integer_scalar_monoid as integer_scalar_monoid,
)
from sage_categories.cat.bimodules import Bimodules as Bimodules
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.native import NativeObjectRealizations as NativeObjectRealizations
from sage_categories.cat.structured_objects import Magmas as Magmas
from sage_categories.cat.structured_objects import Monoids as Monoids
from sage_categories.engines import free_algebras as free_algebras
from sage_categories.engines.presented_modules import tensor_object as tensor_object

__all__ = [
    "IntegerFreeAssociativeConstruction",
    "free_associative_coefficients",
    "free_associative_element",
    "free_associative_generator",
    "free_associative_product",
    "free_associative_substitution",
    "free_associative_underlying_module",
    "free_associative_underlying_morphism",
    "integer_free_associative_algebra",
]
type Word = tuple[int, ...]

@dataclass(frozen=True, eq=False, slots=True)
class IntegerFreeAssociativeConstruction:
    names: tuple[str, ...]
    word_module: CategoryOfCategories.ElementType

def integer_free_associative_algebra(names: Sequence[str] = ("x", "y")): ...
def free_associative_underlying_module(algebra): ...
def free_associative_element(algebra, terms: Mapping[Word, int]): ...
def free_associative_generator(algebra, position: int): ...
def free_associative_coefficients(algebra, element) -> dict[Word, int]: ...
def free_associative_product(algebra, left, right): ...
def free_associative_substitution(algebra, images: Sequence[CategoryOfCategories.ElementType]): ...
def free_associative_underlying_morphism(algebra_morphism): ...
