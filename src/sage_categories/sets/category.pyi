import sage_categories
from _typeshed import Incomplete
from collections.abc import Callable, Iterable
from sage.misc.cachefunc import cached_method
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.cat.predicates import UnknownClass
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.sets.cardinals import CardinalObject
from sage_categories.sets.elements import Datum, SetElementDeclaration
from sage_categories.sets.finite_subsets import FiniteSubsetsCategory, FinitelySupportedFunctionsCategory, SizedSubsetsCategory
from sage_categories.sets.maps import Rule, SetMapDeclaration
from sage_categories.sets.objects import FiniteSetObject, MembershipRule, SetObjectDeclaration
from sage_categories.sets.power_objects import PowerObjectsCategory
from sage_categories.sets.subobjects import ChosenQuotientsCategory, ChosenSubsetsCategory
from typing import overload
__all__ = ['SetsCategory', 'SetObject', 'SetElement', 'SetMap', 'Sets']

class FiniteSets(PropertySubcategory[[Rule], []]):
    ObjectType = FiniteSetObject

    class ElementType(sage_categories.cat.properties.PropertySubcategory.ElementType, sage_categories.sets.elements.SetElementDeclaration, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.properties.PropertySubcategory.MorphismType, sage_categories.sets.maps.SetMapDeclaration, sage_categories.kernel.roles.MorphismOfCategory):
        ...

    def __init__(self, ambient: Category[[Rule], []], name: str, implications: tuple[Category, ...]) -> None:
        ...

    def __call__(self, members: SetObject | Iterable[Datum]) -> SetObject:
        ...

    def construction_owner(self) -> Category:
        ...

    def from_enumeration(self, members: Iterable[Datum]) -> SetObject:
        ...

    def has_chosen_enumeration(self, finite_set: SetObject) -> bool:
        ...

    def chosen_enumeration(self, finite_set: SetObject) -> tuple[Datum, ...]:
        ...

class SetsCategory(Category[[Rule], []]):
    ObjectType = SetObjectDeclaration
    ElementType = SetElementDeclaration
    MorphismType = SetMapDeclaration

    def __init__(self) -> None:
        ...

    def __call__(self, membership_rule: MembershipRule) -> SetObject:
        ...

    def with_cardinality(self, membership_rule: MembershipRule, cardinality: CardinalObject) -> SetObject:
        ...

    def rule_valued(self, membership_rule: MembershipRule, cardinality: CardinalObject | UnknownClass) -> SetObject:
        ...

    def points_by_rule(self, member_object: SetObject) -> bool:
        ...

    def subobjects_type(self) -> type:
        ...

    def Inhabited(self) -> Category[[Rule], []]:
        ...

    def Finite(self) -> FiniteSets:
        ...

    def Infinite(self) -> Category[[Rule], []]:
        ...

    def Countable(self) -> Category[[Rule], []]:
        ...

    def Uncountable(self) -> Category[[Rule], []]:
        ...

    @cached_method
    def ChosenSubsets(self) -> ChosenSubsetsCategory:
        ...

    @cached_method
    def ChosenQuotients(self) -> ChosenQuotientsCategory:
        ...

    @cached_method
    def Empty(self) -> SetObject:
        ...

    @cached_method
    def Initial(self) -> SetObject:
        ...

    @cached_method
    def Terminal(self) -> SetObject:
        ...

    @cached_method
    def Simplex(self, dimension: int) -> SetObject:
        ...

    @cached_method
    def CardinalityFunctor(self) -> Functor:
        ...

    def element_from_defining_morphism(self, defining_morphism: SetMap) -> SetElement:
        ...

    @overload
    def construct_morphism(self, domain: SetObject, codomain: SetObject, rule: Rule) -> SetMap:
        ...

    @overload
    def construct_morphism(self, domain: SetObject, codomain: SetObject, rule: Rule, inverse_rule: Rule) -> SetMap:
        ...

    def construct_identity(self, member_object: SetObject) -> SetMap:
        ...

    def composite(self, second: SetMap, first: SetMap) -> SetMap:
        ...

    def inverse_morphism(self, morphism: SetMap) -> SetMap:
        ...

    def limit_construction(self, shape: Category) -> Callable[[Functor], SetObject]:
        ...

    def colimit_construction(self, shape: Category) -> Callable[[Functor], SetObject]:
        ...

    def exponential(self, exponent: SetObject, base: SetObject) -> SetObject:
        ...

    @cached_method
    def PowerObjects(self) -> PowerObjectsCategory:
        ...

    @cached_method
    def FiniteSubsets(self) -> FiniteSubsetsCategory:
        ...

    @cached_method
    def SubsetsOfSize(self, size: int) -> SizedSubsetsCategory:
        ...

    @cached_method
    def FinitelySupportedFunctions(self) -> FinitelySupportedFunctionsCategory:
        ...

    def name_of(self, set_map: SetMap) -> SetElement:
        ...

    def evaluation(self, exponent: SetObject, base: SetObject) -> SetMap:
        ...

    def transpose(self, set_map: SetMap) -> SetMap:
        ...
SetObject: Incomplete
SetElement: Incomplete
SetMap: Incomplete

def Sets() -> SetsCategory:
    ...
