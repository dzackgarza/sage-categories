from collections.abc import Hashable
from dataclasses import dataclass
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Predicate as Predicate, predicate as predicate
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
type Key = tuple[Hashable, ...]
preserves_magma_operation: Predicate

@dataclass(frozen=True, eq=False, slots=True)
class MagmaObjectData:
    carrier: CategoryOfCategories.ElementType
    multiplication: MorphismCategory.ObjectType

    @property
    def action_morphism(self) -> MorphismCategory.ObjectType:
        ...

class MagmaObjectDeclaration:

    def __init__(self, data: MagmaObjectData) -> None:
        ...

    def carrier(self) -> CategoryOfCategories.ElementType:
        ...

    def multiplication(self) -> MorphismCategory.ObjectType:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class MagmaMorphismData:
    carrier_morphism: MorphismCategory.ObjectType

class MagmaMorphismDeclaration:

    def __init__(self, data: MagmaMorphismData) -> None:
        ...

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        ...

class MagmasCategory(Category[[], []]):
    ObjectType = MagmaObjectDeclaration
    MorphismType = MagmaMorphismDeclaration

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

    def Commutative(self) -> PropertySubcategory:
        ...

    def product_projection(self, index: int) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def construct_morphism(self, domain: MagmasCategory.ObjectType, codomain: MagmasCategory.ObjectType, carrier_morphism: MorphismCategory.ObjectType) -> MagmasCategory.MorphismType:
        ...

    def __call__(self, carrier: CategoryOfCategories.ElementType, multiplication: MorphismCategory.ObjectType) -> MagmasCategory.ObjectType:
        ...

def Magmas(ambient: Category) -> MagmasCategory:
    ...
