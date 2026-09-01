import sage_categories
from _typeshed import Incomplete
from collections.abc import Callable
from dataclasses import dataclass
from sage.misc.cachefunc import cached_method
from sage.rings.integer import Integer
from sage.structure.element import Element
from sage.structure.element_wrapper import ElementWrapper
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage_categories.algebra.semirings import SemiringsCategory
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import AppliedPredicate, Decision, Predicate, Query
from sage_categories.ordinals.category import OrdinalObject
from sage_categories.sets.category import SetMap
from sage_categories.sets.category import SetObject
__all__ = ['generalized_continuum_hypothesis', 'at_most', 'less_than', 'CardinalObject', 'CardinalElement', 'CardinalityMorphism', 'cardinality_query', 'Cardinal', 'CardinalOrder', 'Aleph', 'InitialOrdinal', 'aleph0', 'continuum', 'representative_bijection', 'cardinality_functor']
type Key = tuple[str | int | Key, ...]
generalized_continuum_hypothesis: Predicate

class AlephElement(ElementWrapper):
    ...

class AlephSemiring(UniqueRepresentation, Parent):
    Element = AlephElement

    def __init__(self) -> None:
        ...

    @cached_method
    def zero(self) -> AlephElement:
        ...
    one = zero

    def le(self, first: AlephElement, second: AlephElement) -> Decision:
        ...

    def maximum(self, first: AlephElement, second: AlephElement) -> AlephElement:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class Power:
    base: CardinalValue
    exponent: CardinalValue

@dataclass(frozen=True, eq=False, slots=True)
class Join:
    terms: tuple[CardinalValue, ...]

class CardinalValue(Element):

    def __init__(self, parent: CardinalSemiring, key: Key, value: Integer | AlephElement | Power | Join) -> None:
        ...

    def __pow__(self, exponent: CardinalValue | int) -> CardinalValue:
        ...

    def aleph_index(self) -> OrdinalObject:
        ...

    def finite_value(self) -> int:
        ...

    def __reduce__(self) -> tuple[Callable[[Key], CardinalValue], tuple[Key]]:
        ...

    def __hash__(self) -> int:
        ...

class CardinalSemiring(UniqueRepresentation, Parent):
    Element = CardinalValue

    def __init__(self) -> None:
        ...

    def retained(self, key: Key) -> CardinalValue:
        ...

    def finite(self, value: int) -> CardinalValue:
        ...

    def aleph(self, index: OrdinalObject | int) -> CardinalValue:
        ...

    @cached_method
    def zero(self) -> CardinalValue:
        ...

    @cached_method
    def one(self) -> CardinalValue:
        ...

    def some_elements(self) -> list[CardinalValue]:
        ...

    def is_finite(self, cardinal: CardinalValue) -> Decision:
        ...

    def is_countable(self, cardinal: CardinalValue) -> Decision:
        ...

    def le(self, first: CardinalValue, second: CardinalValue) -> Decision:
        ...

    def add(self, first: CardinalValue, second: CardinalValue) -> CardinalValue:
        ...

    def multiply(self, first: CardinalValue, second: CardinalValue) -> CardinalValue:
        ...

    def power(self, base: CardinalValue, exponent: CardinalValue) -> CardinalValue:
        ...

    def join(self, *cardinals: CardinalValue) -> CardinalValue:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class CardinalObjectData:
    value: CardinalValue

@dataclass(frozen=True, eq=False, slots=True)
class CardinalMorphismData:
    set_map: SetMap

class CardinalObjectDeclaration(sage_categories.sets.objects.SetObjectDeclaration, sage_categories.kernel.roles.ObjectOfCategory):

    def __init__(self, data: CardinalObjectData) -> None:
        ...

    def aleph_index(self) -> OrdinalObject:
        ...

    def initial_ordinal(self) -> OrdinalObject:
        ...

    def cardinality(self) -> CardinalObject:
        ...

    def is_finite(self) -> AppliedPredicate:
        ...

    def is_infinite(self) -> AppliedPredicate:
        ...

    def is_countable(self) -> AppliedPredicate:
        ...

    def is_uncountable(self) -> AppliedPredicate:
        ...

    def __add__(self, other: CardinalObject | int) -> CardinalObject:
        ...

    def __radd__(self, other: int) -> CardinalObject:
        ...

    def __mul__(self, other: CardinalObject | int) -> CardinalObject:
        ...

    def __rmul__(self, other: int) -> CardinalObject:
        ...

    def __pow__(self, exponent: CardinalObject | int) -> CardinalObject:
        ...

    def __rpow__(self, base: int) -> CardinalObject:
        ...

    def __mod__(self, other: CardinalObject | int) -> CardinalObject:
        ...

    def __rmod__(self, other: int) -> CardinalObject:
        ...

    def __le__(self, other: CardinalObject | int) -> AppliedPredicate:
        ...

    def __lt__(self, other: CardinalObject | int) -> AppliedPredicate:
        ...

    def __ge__(self, other: CardinalObject | int) -> AppliedPredicate:
        ...

    def __gt__(self, other: CardinalObject | int) -> AppliedPredicate:
        ...

class CardinalMorphismDeclaration(sage_categories.sets.maps.SetMapDeclaration, sage_categories.kernel.roles.MorphismOfCategory):

    def __init__(self, data: CardinalMorphismData) -> None:
        ...
at_most: Predicate
less_than: Predicate

class CardinalCategory(Category[[MorphismCategory.ObjectType], []]):
    ObjectType = CardinalObjectDeclaration
    MorphismType = CardinalMorphismDeclaration

    class ElementType(sage_categories.sets.elements.SetElementDeclaration, sage_categories.kernel.roles.ElementOfObject):
        ...

    def __init__(self) -> None:
        ...

    def Finite(self) -> Category:
        ...

    def Infinite(self) -> Category:
        ...

    def Countable(self) -> Category:
        ...

    def Uncountable(self) -> Category:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    @cached_method
    def representative_functor(self) -> Functor:
        ...

    def representative(self, cardinal: CardinalObject) -> SetObject:
        ...

    def __call__(self, value: CardinalObject | int) -> CardinalObject:
        ...

    def aleph(self, index: OrdinalObject | int) -> CardinalObject:
        ...

    def zero(self) -> CardinalObject:
        ...

    def one(self) -> CardinalObject:
        ...

    def supremum(self, *cardinals: CardinalObject) -> CardinalObject:
        ...

    def sum(self, first: CardinalObject, second: CardinalObject) -> CardinalObject:
        ...

    def product(self, first: CardinalObject, second: CardinalObject) -> CardinalObject:
        ...

    def power(self, base: CardinalObject, exponent: CardinalObject) -> CardinalObject:
        ...

    def construct_morphism(self, domain: CardinalObject, codomain: CardinalObject, set_map: SetMap) -> CardinalityMorphism:
        ...

    def construct_identity(self, cardinal: CardinalObject) -> CardinalityMorphism:
        ...

    def composite(self, second: CardinalityMorphism, first: CardinalityMorphism) -> CardinalityMorphism:
        ...

    def inverse_morphism(self, morphism: CardinalityMorphism) -> CardinalityMorphism:
        ...

    def semiring_object(self) -> SemiringsCategory.ObjectType:
        ...
CardinalObject: Incomplete
CardinalElement: Incomplete
CardinalityMorphism: Incomplete
cardinality_query: Query

def Cardinal() -> CardinalCategory:
    ...

def CardinalOrder() -> Category:
    ...
Aleph: Functor
InitialOrdinal: Functor
aleph0: CardinalObject
continuum: CardinalObject

def representative_bijection(member_object: SetObject) -> SetMap:
    ...

def cardinality_functor() -> Functor:
    ...
