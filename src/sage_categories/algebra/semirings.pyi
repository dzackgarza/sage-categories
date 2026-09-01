from dataclasses import dataclass
from sage_categories.algebra.monoids import Monoids as Monoids
from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.kernel.refinement import refine as refine
from sage_categories.sets.category import Sets as Sets
from typing import Any

@dataclass(frozen=True, eq=False)
class SemiringObjectData:
    carrier: Any
    addition: Any
    zero: Any
    multiplication: Any
    one: Any

    @property
    def unit(self) -> Any:
        ...

class SemiringObjectDeclaration:

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

@dataclass(frozen=True, eq=False, slots=True)
class SemiringMorphismData:
    carrier_morphism: Any

class SemiringMorphismDeclaration:

    def __init__(self, data: SemiringMorphismData) -> None:
        ...

    def carrier_morphism(self) -> Any:
        ...

class SemiringsCategory(Category[[], []]):
    ObjectType = SemiringObjectDeclaration
    MorphismType = SemiringMorphismDeclaration

    class ElementType:
        ...

    def __init__(self, ambient: Category) -> None:
        ...

    def ambient(self) -> Category:
        ...

    def additive_monoid_projection(self) -> Functor:
        ...

    def multiplicative_monoid_projection(self) -> Functor:
        ...

    def product_projection(self, index: int) -> Functor:
        ...

    def structure_functors(self) -> tuple[Any, ...]:
        ...

    def construct_morphism(self, domain: SemiringsCategory.ObjectType, codomain: SemiringsCategory.ObjectType, carrier_morphism: Any) -> SemiringsCategory.MorphismType:
        ...

    def __call__(self, carrier: Any, addition: Any, zero: Any, multiplication: Any, one: Any) -> SemiringsCategory.ObjectType:
        ...

def Semirings(ambient: Category | None=None) -> SemiringsCategory:
    ...
