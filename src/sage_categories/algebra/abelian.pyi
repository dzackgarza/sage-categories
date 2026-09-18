from collections.abc import Callable, Hashable
from dataclasses import dataclass

from sage_categories.algebra._firewall.abelian import Engine as Engine
from sage_categories.cat.assembly import chosen_construction as chosen_construction
from sage_categories.cat.assembly import has_selected_value as has_selected_value
from sage_categories.cat.assembly import select_value as select_value
from sage_categories.cat.assembly import selected_value as selected_value
from sage_categories.cat.bimodules import Bimodules as Bimodules
from sage_categories.cat.calculus import binary_product_data as binary_product_data
from sage_categories.cat.calculus import natural_isomorphism as natural_isomorphism
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.certified_structures import (
    certified_additive_group as certified_additive_group,
)
from sage_categories.cat.cones import ConeCategory as ConeCategory
from sage_categories.cat.cones import cocone as cocone
from sage_categories.cat.cones import cocone_apex as cocone_apex
from sage_categories.cat.cones import cone as cone
from sage_categories.cat.cones import cone_apex as cone_apex
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.diagrams import from_sequence as from_sequence
from sage_categories.cat.diagrams import sequence_position as sequence_position
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.limit_basis import parallel_pair as parallel_pair
from sage_categories.cat.monoidal import Cartesian as Cartesian
from sage_categories.cat.monoidal import MonoidalStructures as MonoidalStructures
from sage_categories.cat.monoidal import (
    MonoidalStructuresCategory as MonoidalStructuresCategory,
)
from sage_categories.cat.monoidal import tensor_parentheses as tensor_parentheses
from sage_categories.cat.monoidal import tensor_units as tensor_units
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Proposition as Proposition
from sage_categories.cat.predicates import ask as ask
from sage_categories.cat.shapes import Discrete as Discrete
from sage_categories.cat.structured_objects import AdditiveGroups as AdditiveGroups
from sage_categories.cat.structured_objects import MonoidCategory as MonoidCategory
from sage_categories.cat.structured_objects import Monoids as Monoids
from sage_categories.engines.presented_modules import tensor_morphism as tensor_morphism

__all__ = [
    "AbelianBimoduleTensor",
    "AbelianGroups",
    "AbelianTensor",
    "abelian_homomorphism",
    "balanced_tensor",
    "bilinear_map",
    "coequalizer_mediator",
    "coequalizer_projection",
    "indexed_free_abelian_coproduct",
    "indexed_free_abelian_group",
    "indexed_free_abelian_injection",
    "indexed_free_abelian_mediator",
    "induced_left_action",
    "induced_right_action",
    "integer_group",
    "presented_abelian_group",
    "relative_left_unitor",
    "relative_right_unitor",
    "relative_tensor",
    "relative_tensor_mediator",
    "relative_tensor_morphism",
    "simple_tensor",
    "tensor_mediator",
]

def AbelianGroups() -> Category: ...
def presented_abelian_group(engine: Engine) -> CategoryOfCategories.ElementType: ...
def integer_group() -> CategoryOfCategories.ElementType: ...
def indexed_free_abelian_group(index_set: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType: ...
def indexed_free_abelian_injection(group: CategoryOfCategories.ElementType, index: Hashable) -> MorphismCategory.ObjectType: ...
def indexed_free_abelian_mediator(
    group: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, component: Callable[[Hashable], MorphismCategory.ObjectType]
) -> MorphismCategory.ObjectType: ...
def indexed_free_abelian_coproduct(index_set: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType: ...
def abelian_homomorphism(
    source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, rule: Callable[[Hashable], Hashable]
) -> MorphismCategory.ObjectType: ...
def coequalizer_projection(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType: ...
def coequalizer_mediator(projection: MorphismCategory.ObjectType, coequalizing: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType: ...
def bilinear_map(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...
def simple_tensor(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, left: Hashable, right: Hashable) -> CategoryOfCategories.ElementType: ...
def tensor_mediator(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    biadditive: Callable[[Hashable, Hashable], Hashable],
) -> MorphismCategory.ObjectType: ...
def AbelianTensor() -> MonoidalStructuresCategory.ObjectType: ...
def relative_tensor(right_action: MorphismCategory.ObjectType, left_action: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType: ...
def balanced_tensor(projection: MorphismCategory.ObjectType, left: Hashable, right: Hashable) -> CategoryOfCategories.ElementType: ...
def relative_tensor_mediator(
    projection: MorphismCategory.ObjectType, target: CategoryOfCategories.ElementType, balanced: Callable[[Hashable, Hashable], Hashable]
) -> MorphismCategory.ObjectType: ...
def induced_left_action(projection: MorphismCategory.ObjectType, left_action: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType: ...
def induced_right_action(projection: MorphismCategory.ObjectType, right_action: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType: ...
def relative_tensor_morphism(
    source: MorphismCategory.ObjectType, target: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType
) -> MorphismCategory.ObjectType: ...
def relative_left_unitor(
    projection: MorphismCategory.ObjectType, left_action: MorphismCategory.ObjectType, unit_morphism: MorphismCategory.ObjectType
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]: ...
def relative_right_unitor(
    projection: MorphismCategory.ObjectType, right_action: MorphismCategory.ObjectType, unit_morphism: MorphismCategory.ObjectType
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]: ...
def AbelianBimoduleTensor(scalars: MonoidCategory.ObjectType) -> MonoidalStructuresCategory.ObjectType: ...

@dataclass(frozen=True, eq=False, slots=True)
class _CoordinateBridge:
    orders: tuple[int, ...]
    coordinates: Callable[[Hashable], tuple[int, ...]]
    element: Callable[[tuple[int, ...]], Hashable]
    factors: tuple[_CoordinateBridge, ...] = ...

    def rank(self) -> int: ...
    def direct_sum(self, factors: tuple[_CoordinateBridge, ...]) -> _CoordinateBridge: ...
    def zero_datum(self) -> Hashable: ...

def _coordinates(group: CategoryOfCategories.ElementType) -> _CoordinateBridge: ...
def _retain_coordinates(group: CategoryOfCategories.ElementType, form: _CoordinateBridge) -> None: ...
def _rule_abelian_homomorphism(
    source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, rule: Callable[[Hashable], Hashable]
) -> MorphismCategory.ObjectType: ...
