from dataclasses import dataclass
from sage_categories.algebra.magmas import Magmas as Magmas
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.predicates import Predicate as Predicate, predicate as predicate
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.sets.category import Sets as Sets
from typing import Any
preserves_monoid_unit: Predicate

@dataclass(frozen=True, eq=False, slots=True)
class MonoidObjectData:
    carrier: Any
    multiplication: Any
    unit: Any

class MonoidObjectDeclaration:

    def __init__(self, data: Any) -> None:
        ...

    def carrier(self) -> Any:
        ...

    def multiplication(self) -> Any:
        ...

    def unit_morphism(self) -> Any:
        ...

    def zero(self) -> Any:
        ...

    def one(self) -> Any:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class MonoidMorphismData:
    carrier_morphism: Any

class MonoidMorphismDeclaration:

    def __init__(self, data: MonoidMorphismData) -> None:
        ...

    def carrier_morphism(self) -> Any:
        ...

class MonoidsCategory(Category[[], []]):
    ObjectType = MonoidObjectDeclaration
    MorphismType = MonoidMorphismDeclaration

    class ElementType:
        ...

    def __init__(self, ambient: Category) -> None:
        ...

    def ambient(self) -> Category:
        ...

    def Additive(self) -> PropertySubcategory:
        ...

    def Multiplicative(self) -> PropertySubcategory:
        ...

    def to_magmas(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Any, ...]:
        ...

    def construct_morphism(self, domain: MonoidsCategory.ObjectType, codomain: MonoidsCategory.ObjectType, carrier_morphism: Any) -> MonoidsCategory.MorphismType:
        ...

    def __call__(self, carrier: Any, multiplication: Any, unit: Any) -> MonoidsCategory.ObjectType:
        ...

def Monoids(ambient: Category | None=None) -> MonoidsCategory:
    ...
