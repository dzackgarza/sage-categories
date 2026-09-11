import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from _typeshed import Incomplete
from collections.abc import Callable, Hashable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from functools import cache
from sage.symbolic.expression import Expression as SageExpression
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition, UnknownClass
from sage_categories.cat.slices import SliceLikeCategory, SliceProperty
from sympy import Lambda
from typing import Literal, Protocol, overload
__all__ = ['Sets', 'MapForm', 'ObjectForm', 'SetsCategory', 'FiniteSets']
type Map = Callable[[Hashable], Hashable]
type MembershipRule = Callable[[Hashable], Proposition]
type MapData = Map | Lambda | SageExpression | Mapping[Hashable, Hashable]

class FinitePredicate(Predicate):
    name: str

class SetMembershipPredicate(Predicate):
    name: str

class _ProductRule:
    factors: Incomplete

    def __init__(self, factors: tuple[SetsCategory.ObjectType, ...]) -> None:
        ...

    def __call__(self, datum: Hashable) -> Proposition:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class _IndexedProductValue:
    diagram: Functor
    rule: Callable[[Hashable], Hashable]

    def component(self, vertex: CategoryOfCategories.ElementType) -> Hashable:
        ...

class _IndexedProductRule:
    diagram: Incomplete

    def __init__(self, diagram: Functor) -> None:
        ...

    def __call__(self, datum: Hashable) -> Proposition:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class _IndexedCoproductValue:
    diagram: Functor
    index: Hashable
    value: Hashable

class _IndexedCoproductRule:
    diagram: Incomplete

    def __init__(self, diagram: Functor) -> None:
        ...

    def __call__(self, datum: Hashable) -> Proposition:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class _SequentialColimitValue:
    diagram: Functor
    stage: Hashable
    value: Hashable

class _SequentialColimitRule:
    diagram: Incomplete

    def __init__(self, diagram: Functor) -> None:
        ...

    def __call__(self, datum: Hashable) -> Proposition:
        ...

class _PredicateRule:

    def __init__(self, ambient: SetsCategory.ObjectType, predicate: Callable[[SetsCategory.ElementType], Proposition]) -> None:
        ...

    def __call__(self, datum: Hashable) -> Proposition:
        ...

class MapForm(Protocol):

    def evaluate(self, datum: Hashable) -> Hashable:
        ...

    def compose(self, first: MapForm) -> MapForm | None:
        ...

    def equals(self, other: MapForm) -> bool | None:
        ...

    def inverse(self) -> MapForm | None:
        ...

class ObjectForm(Protocol):

    def identity(self) -> MapForm:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class _SetMap:
    action: Map
    rule: Lambda | None
    form: MapForm | None = ...

class SetsCategory(Category[[Map], []]):

    def structure_functors(self) -> tuple[Functor, ...]:
        ...
    Finite: Incomplete

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, presentation: tuple[Hashable, ...] | MembershipRule) -> None:
            ...

        def set_presentation(self) -> tuple[Hashable, ...] | MembershipRule:
            ...

        def representative(self, datum: Hashable) -> Hashable:
            ...

        @cache
        def point(self, datum: Hashable) -> SetsCategory.ElementType:
            ...

        def __iter__(self) -> Iterator[SetsCategory.ElementType]:
            ...

        def __len__(self) -> int:
            ...

        def __contains__(self, point: CategoryOfCategories.ElementType) -> bool:
            ...

        def membership_proposition(self, point: CategoryOfCategories.ElementType) -> Proposition:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):

        def __init__(self, datum: Hashable) -> None:
            ...

        def datum(self) -> Hashable:
            ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: Map | _SetMap) -> None:
            ...

        def __call__(self, point: CategoryOfCategories.ElementType) -> SetsCategory.ElementType:
            ...

        def domain(self) -> SetsCategory.ObjectType:
            ...

        def codomain(self) -> SetsCategory.ObjectType:
            ...

    def inverse_morphism(self, morphism: SetsCategory.MorphismType) -> SetsCategory.MorphismType:
        ...

    @overload
    def __call__(self) -> SetsCategory:
        ...

    @overload
    def __call__(self, values: Iterable[Hashable]) -> SetsCategory.ObjectType:
        ...

    def from_membership(self, rule: MembershipRule) -> SetsCategory.ObjectType:
        ...

    def has_chosen_enumeration(self, value: SetsCategory.ObjectType) -> bool:
        ...

    def chosen_enumeration(self, value: SetsCategory.ObjectType) -> MorphismCategory.ObjectType | UnknownClass:
        ...

    def finite_points(self, value: SetsCategory.ObjectType) -> tuple[SetsCategory.ElementType, ...] | UnknownClass:
        ...

    def enumeration_index_inclusion(self, enumeration: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def retain_enumeration(self, enumeration: MorphismCategory.ObjectType, inclusion: MorphismCategory.ObjectType) -> None:
        ...

    def constant(self, source: SetsCategory.ObjectType, point: SetsCategory.ElementType) -> SetsCategory.MorphismType:
        ...

    def retain_form(self, value: SetsCategory.ObjectType, form: ObjectForm) -> None:
        ...

    def form_of(self, value: SetsCategory.ObjectType) -> ObjectForm | None:
        ...

    def map_form(self, arrow: SetsCategory.MorphismType) -> MapForm | None:
        ...

    def Initial(self) -> SetsCategory.ObjectType:
        ...

    def subobjects_type(self) -> type[SetSubobjects]:
        ...

    def Terminal(self) -> SetsCategory.ObjectType:
        ...

    def point_morphism(self, point: SetsCategory.ElementType) -> SetsCategory.MorphismType:
        ...

    def element_from_defining_morphism(self, arrow: MorphismCategory.ObjectType) -> SetsCategory.ElementType:
        ...

    def construct_morphism(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, action: MapData | _SetMap) -> MorphismCategory.ObjectType:
        ...

    def construct_identity(self, value: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

    def colimit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

    def image_factorization(self, arrow: MorphismCategory.ObjectType) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
        ...

    def factor_through_monomorphism(self, mono: MorphismCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType | Literal[False]:
        ...

    @cache
    def hom_morphisms(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType) -> tuple[MorphismCategory.ObjectType, ...]:
        ...

class SetSubobjects(SliceProperty):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> SetSubobjects.ObjectType:
            ...

        def codomain(self) -> SetSubobjects.ObjectType:
            ...

    def from_predicate(self, predicate: Callable[[SetsCategory.ElementType], Proposition]) -> SliceLikeCategory.ObjectType:
        ...
FiniteSets: Incomplete

def _finite_data(value: SetsCategory.ObjectType) -> tuple[Hashable, ...] | UnknownClass:
    ...
