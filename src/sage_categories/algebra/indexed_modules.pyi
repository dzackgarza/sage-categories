from collections.abc import Hashable, Mapping
from sage_categories.algebra.abelian import AbelianGroups as AbelianGroups, AbelianTensor as AbelianTensor, abelian_homomorphism as abelian_homomorphism, coequalizer_mediator as coequalizer_mediator, coequalizer_projection as coequalizer_projection, indexed_free_abelian_coproduct as indexed_free_abelian_coproduct, indexed_free_abelian_injection as indexed_free_abelian_injection, indexed_free_abelian_mediator as indexed_free_abelian_mediator, integer_group as integer_group, presented_abelian_group as presented_abelian_group
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import ConeCategory as ConeCategory, cocone as cocone
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.modules import ModuleCategory as ModuleCategory, Modules as Modules
from sage_categories.cat.monoidal import SelfAction as SelfAction
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.cat.shapes import Discrete as Discrete
from sage_categories.cat.structured_objects import Monoids as Monoids
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function
from sage_categories.sets.finite import Sets as Sets

def integer_scalar_monoid() -> CategoryOfCategories.ElementType:
    ...

def integer_regular_module() -> ModuleCategory.ObjectType:
    ...

def indexed_free_integer_module(index_set: CategoryOfCategories.ElementType) -> ModuleCategory.ObjectType:
    ...

def indexed_free_integer_element(module: ModuleCategory.ObjectType, terms: Mapping[Hashable, int]) -> CategoryOfCategories.ElementType:
    ...

def indexed_free_integer_support(module: ModuleCategory.ObjectType, element: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    ...

def indexed_free_integer_coefficients(module: ModuleCategory.ObjectType, element: CategoryOfCategories.ElementType) -> dict[Hashable, int]:
    ...

def indexed_free_integer_homomorphism(source: ModuleCategory.ObjectType, target: ModuleCategory.ObjectType, basis_image) -> MorphismCategory.ObjectType:
    ...

def integer_module(additive_group: CategoryOfCategories.ElementType) -> ModuleCategory.ObjectType:
    ...

@cached_function
def finite_free_integer_module(rank: int) -> ModuleCategory.ObjectType:
    ...

class IntegerModulePresentation:

    def __init__(self, relation_rows) -> None:
        ...

    def relation_matrix(self):
        ...

    def module_category(self):
        ...

    def source_free_module(self):
        ...

    def target_free_module(self):
        ...

    def relation_morphism(self):
        ...

    def zero_morphism(self):
        ...

    def module(self):
        ...

    def cokernel_projection(self):
        ...

    def target_basis_element(self, index: int):
        ...

    def factor(self, target: ModuleCategory.ObjectType, coequalizing: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

def presented_integer_module(relation_rows) -> IntegerModulePresentation:
    ...
