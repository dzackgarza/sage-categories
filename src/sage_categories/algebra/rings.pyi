from dataclasses import dataclass
from sage_categories.algebra.groups import Groups as Groups
from sage_categories.algebra.semirings import Semirings as Semirings
from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.kernel.refinement import refine as refine
from sage_categories.sets.category import Sets as Sets
from typing import Any

@dataclass(frozen=True, eq=False)
class RingObjectData:
    carrier: Any
    addition: Any
    zero: Any
    multiplication: Any
    one: Any
    inversion: Any

    @property
    def unit(self) -> Any:
        ...

class RingObjectDeclaration:

    def __init__(self, data: Any) -> None:
        ...

    def carrier(self) -> Any:
        ...

    def addition(self) -> Any:
        ...

    def zero(self) -> Any:
        ...

    def multiplication(self) -> Any:
        ...

    def one(self) -> Any:
        ...

    def inversion(self) -> Any:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class RingMorphismData:
    carrier_morphism: Any

class RingMorphismDeclaration:

    def __init__(self, data: RingMorphismData) -> None:
        ...

    def carrier_morphism(self) -> Any:
        ...

class RingsCategory(Category[[], []]):
    ObjectType = RingObjectDeclaration
    MorphismType = RingMorphismDeclaration

    class ElementType:
        ...

    def __init__(self, ambient: Category) -> None:
        ...

    def ambient(self) -> Category:
        ...

    def Commutative(self) -> PropertySubcategory:
        ...

    def semiring_projection(self) -> Functor:
        ...

    def additive_group_projection(self) -> Functor:
        ...

    def product_projection(self, index: int) -> Functor:
        ...

    def structure_functors(self) -> tuple[Any, ...]:
        ...

    def construct_morphism(self, domain: RingsCategory.ObjectType, codomain: RingsCategory.ObjectType, carrier_morphism: Any) -> RingsCategory.MorphismType:
        ...

    def __call__(self, carrier: Any, addition: Any, zero: Any, multiplication: Any, one: Any, inversion: Any) -> RingsCategory.ObjectType:
        ...

def Rings(ambient: Category | None=None) -> RingsCategory:
    ...
