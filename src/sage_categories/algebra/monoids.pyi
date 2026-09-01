from collections.abc import Hashable
from dataclasses import dataclass
from sage_categories.algebra.magmas import MagmaObjectData as MagmaObjectData, Magmas as Magmas, MagmasCategory as MagmasCategory
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Predicate as Predicate, predicate as predicate
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
type Key = tuple[Hashable, ...]
preserves_monoid_unit: Predicate

@dataclass(frozen=True, eq=False, slots=True)
class MonoidObjectData(MagmaObjectData):
    unit: MorphismCategory.ObjectType | CategoryOfCategories.ElementType

class MonoidObjectDeclaration:

    def __init__(self, data: MonoidObjectData) -> None:
        ...

    def carrier(self) -> CategoryOfCategories.ElementType:
        ...

    def multiplication(self) -> MorphismCategory.ObjectType:
        ...

    def unit_morphism(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        ...

    def zero(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        ...

    def one(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class MonoidMorphismData:
    carrier_morphism: MorphismCategory.ObjectType

class MonoidMorphismDeclaration:

    def __init__(self, data: MonoidMorphismData) -> None:
        ...

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
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

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def construct_morphism(self, domain: MonoidsCategory.ObjectType, codomain: MonoidsCategory.ObjectType, carrier_morphism: MorphismCategory.ObjectType) -> MonoidsCategory.MorphismType:
        ...

    def __call__(self, carrier: CategoryOfCategories.ElementType, multiplication: MorphismCategory.ObjectType, unit: MorphismCategory.ObjectType | CategoryOfCategories.ElementType) -> MonoidsCategory.ObjectType:
        ...

def Monoids(ambient: Category) -> MonoidsCategory:
    ...
