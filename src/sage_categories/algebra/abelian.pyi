from collections.abc import Callable, Hashable
from dataclasses import dataclass
from sage.combinat.free_module import CombinatorialFreeModule
from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup_class
from sage.modules.fg_pid.fgp_module import FGP_Module_class
from sage.structure.parent import Parent
from sage_categories.cat.bimodules import Bimodules as Bimodules
from sage_categories.cat.calculus import binary_product_data as binary_product_data, natural_isomorphism as natural_isomorphism
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import ConeCategory as ConeCategory, cocone as cocone, cocone_apex as cocone_apex, cone as cone, cone_apex as cone_apex
from sage_categories.cat.diagrams import from_sequence as from_sequence, sequence_position as sequence_position
from sage_categories.cat.functors import Cat as Cat, Fun as Fun, Functor as Functor
from sage_categories.cat.limit_basis import parallel_pair as parallel_pair
from sage_categories.cat.monoidal import Cartesian as Cartesian, MonoidalStructures as MonoidalStructures, MonoidalStructuresCategory as MonoidalStructuresCategory, tensor_morphism as tensor_morphism, tensor_parentheses as tensor_parentheses, tensor_units as tensor_units
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Proposition as Proposition, ask as ask
from sage_categories.cat.shapes import Discrete as Discrete
from sage_categories.cat.structured_objects import AdditiveGroups as AdditiveGroups, Groups as Groups, Magmas as Magmas, MonoidCategory as MonoidCategory, Monoids as Monoids, PointedMagmas as PointedMagmas
from sage_categories.kernel.refinement import refine as refine
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict, cached_function as cached_function
from sage_categories.kernel.type_aliases import ContainmentInput as ContainmentInput
from sage_categories.sets.finite import Sets as Sets
type Engine = AdditiveAbelianGroup_class | FGP_Module_class

def AbelianGroups() -> Category:
    ...

def presented_abelian_group(engine: Engine) -> CategoryOfCategories.ElementType:
    ...

def integer_group() -> CategoryOfCategories.ElementType:
    ...

def indexed_free_abelian_group(index_set: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    ...

def indexed_free_abelian_injection(group: CategoryOfCategories.ElementType, index: Hashable) -> MorphismCategory.ObjectType:
    ...

def indexed_free_abelian_mediator(group: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, component: Callable[[Hashable], MorphismCategory.ObjectType]) -> MorphismCategory.ObjectType:
    ...

def indexed_free_abelian_coproduct(index_set: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    ...

def abelian_homomorphism(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, rule: Callable[[Hashable], Hashable]) -> MorphismCategory.ObjectType:
    ...

def coequalizer_projection(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def coequalizer_mediator(projection: MorphismCategory.ObjectType, coequalizing: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def bilinear_map(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
    ...

def simple_tensor(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, left: Hashable, right: Hashable) -> CategoryOfCategories.ElementType:
    ...

def tensor_mediator(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, biadditive: Callable[[Hashable, Hashable], Hashable]) -> MorphismCategory.ObjectType:
    ...

def AbelianTensor() -> MonoidalStructuresCategory.ObjectType:
    ...

def relative_tensor(right_action: MorphismCategory.ObjectType, left_action: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def balanced_tensor(projection: MorphismCategory.ObjectType, left: Hashable, right: Hashable) -> CategoryOfCategories.ElementType:
    ...

def relative_tensor_mediator(projection: MorphismCategory.ObjectType, target: CategoryOfCategories.ElementType, balanced: Callable[[Hashable, Hashable], Hashable]) -> MorphismCategory.ObjectType:
    ...

def induced_left_action(projection: MorphismCategory.ObjectType, left_action: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def induced_right_action(projection: MorphismCategory.ObjectType, right_action: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def relative_tensor_morphism(source: MorphismCategory.ObjectType, target: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def relative_left_unitor(projection: MorphismCategory.ObjectType, left_action: MorphismCategory.ObjectType, unit_morphism: MorphismCategory.ObjectType) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    ...

def relative_right_unitor(projection: MorphismCategory.ObjectType, right_action: MorphismCategory.ObjectType, unit_morphism: MorphismCategory.ObjectType) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    ...

def AbelianBimoduleTensor(scalars: MonoidCategory.ObjectType) -> MonoidalStructuresCategory.ObjectType:
    ...

@dataclass(frozen=True, eq=False, slots=True)
class _CoordinateBridge:
    orders: tuple[int, ...]
    coordinates: Callable[[Hashable], tuple[int, ...]]
    element: Callable[[tuple[int, ...]], Hashable]
    factors: tuple[_CoordinateBridge, ...] = ...

    def rank(self) -> int:
        ...

    def direct_sum(self, factors: tuple[_CoordinateBridge, ...]) -> _CoordinateBridge:
        ...

    def zero_datum(self) -> Hashable:
        ...

def _coordinates(group: CategoryOfCategories.ElementType) -> _CoordinateBridge:
    ...

@dataclass(frozen=True, eq=False, slots=True)
class _IndexedFreeAbelianData:
    index_set: CategoryOfCategories.ElementType
    engine: CombinatorialFreeModule

def _rule_abelian_homomorphism(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, rule: Callable[[Hashable], Hashable]) -> MorphismCategory.ObjectType:
    ...

def _indexed_free_record(group: CategoryOfCategories.ElementType) -> _IndexedFreeAbelianData:
    ...
