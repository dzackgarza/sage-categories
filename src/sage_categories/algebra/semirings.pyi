from collections.abc import Hashable
from dataclasses import dataclass
from sage.rings.integer import Integer
from sage_categories.algebra.monoids import Monoids as Monoids, MonoidsCategory as MonoidsCategory
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.kernel.refinement import refine as refine
type Key = tuple[Hashable, ...]

@dataclass(frozen=True, eq=False)
class SemiringObjectData:
    carrier: CategoryOfCategories.ElementType
    addition: MorphismCategory.ObjectType
    zero: MorphismCategory.ObjectType | CategoryOfCategories.ElementType
    multiplication: MorphismCategory.ObjectType
    one: MorphismCategory.ObjectType | CategoryOfCategories.ElementType

    @property
    def unit(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        ...

class SemiringObjectDeclaration:

    def __init__(self, data: SemiringObjectData) -> None:
        ...

    def carrier(self) -> CategoryOfCategories.ElementType:
        ...

    def addition(self) -> MorphismCategory.ObjectType:
        ...

    def zero(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        ...

    def multiplication(self) -> MorphismCategory.ObjectType:
        ...

    def one(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class SemiringMorphismData:
    carrier_morphism: MorphismCategory.ObjectType

class SemiringMorphismDeclaration:

    def __init__(self, data: SemiringMorphismData) -> None:
        ...

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
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

    def product_projection(self, index: int | Integer) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def construct_morphism(self, domain: SemiringsCategory.ObjectType, codomain: SemiringsCategory.ObjectType, carrier_morphism: MorphismCategory.ObjectType) -> SemiringsCategory.MorphismType:
        ...

    def __call__(self, carrier: CategoryOfCategories.ElementType, addition: MorphismCategory.ObjectType, zero: MorphismCategory.ObjectType | CategoryOfCategories.ElementType, multiplication: MorphismCategory.ObjectType, one: MorphismCategory.ObjectType | CategoryOfCategories.ElementType) -> SemiringsCategory.ObjectType:
        ...

def Semirings(ambient: Category) -> SemiringsCategory:
    ...
