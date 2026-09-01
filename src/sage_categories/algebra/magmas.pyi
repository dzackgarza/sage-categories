from dataclasses import dataclass
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.predicates import Predicate as Predicate, predicate as predicate
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.sets.category import Sets as Sets
from typing import Any
preserves_magma_operation: Predicate

@dataclass(frozen=True, eq=False, slots=True)
class MagmaObjectData:
    carrier: Any
    multiplication: Any

class MagmaObjectDeclaration:

    def __init__(self, data: Any) -> None:
        ...

    def carrier(self) -> Any:
        ...

    def multiplication(self) -> Any:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class MagmaMorphismData:
    carrier_morphism: Any

class MagmaMorphismDeclaration:

    def __init__(self, data: MagmaMorphismData) -> None:
        ...

    def carrier_morphism(self) -> Any:
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

    def structure_functors(self) -> tuple[Any, ...]:
        ...

    def construct_morphism(self, domain: MagmasCategory.ObjectType, codomain: MagmasCategory.ObjectType, carrier_morphism: Any) -> MagmasCategory.MorphismType:
        ...

    def __call__(self, carrier: Any, multiplication: Any) -> MagmasCategory.ObjectType:
        ...

def Magmas(ambient: Category | None=None) -> MagmasCategory:
    ...
