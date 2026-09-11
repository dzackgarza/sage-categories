from collections.abc import Hashable, Mapping

from sage_categories.algebra.abelian import (
    AbelianGroups as AbelianGroups,
)
from sage_categories.algebra.abelian import (
    AbelianTensor as AbelianTensor,
)
from sage_categories.algebra.abelian import (
    indexed_free_abelian_coproduct as indexed_free_abelian_coproduct,
)
from sage_categories.algebra.abelian import (
    indexed_free_abelian_injection as indexed_free_abelian_injection,
)
from sage_categories.algebra.abelian import (
    indexed_free_abelian_mediator as indexed_free_abelian_mediator,
)
from sage_categories.algebra.abelian import (
    integer_group as integer_group,
)
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import cocone as cocone
from sage_categories.cat.cones import cocone_apex as cocone_apex
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.modules import ModuleCategory as ModuleCategory
from sage_categories.cat.modules import Modules as Modules
from sage_categories.cat.monoidal import SelfAction as SelfAction
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.shapes import Discrete as Discrete
from sage_categories.cat.structured_objects import Monoids as Monoids
from sage_categories.kernel.refinement import refine as refine
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = [
    "indexed_free_integer_coefficients",
    "indexed_free_integer_element",
    "indexed_free_integer_homomorphism",
    "indexed_free_integer_module",
    "indexed_free_integer_support",
    "integer_regular_module",
    "integer_scalar_monoid",
]

def integer_scalar_monoid() -> CategoryOfCategories.ElementType: ...
def integer_regular_module() -> ModuleCategory.ObjectType: ...
def indexed_free_integer_module(index_set: CategoryOfCategories.ElementType) -> ModuleCategory.ObjectType: ...
def indexed_free_integer_element(module: ModuleCategory.ObjectType, terms: Mapping[Hashable, int]) -> CategoryOfCategories.ElementType: ...
def indexed_free_integer_support(module: ModuleCategory.ObjectType, element: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType: ...
def indexed_free_integer_coefficients(module: ModuleCategory.ObjectType, element: CategoryOfCategories.ElementType) -> dict[Hashable, int]: ...
def indexed_free_integer_homomorphism(source: ModuleCategory.ObjectType, target: ModuleCategory.ObjectType, basis_image) -> MorphismCategory.ObjectType: ...
