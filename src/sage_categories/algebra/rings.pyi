from collections.abc import Hashable
from dataclasses import dataclass
from sage_categories.algebra.groups import Groups as Groups, GroupsCategory as GroupsCategory
from sage_categories.algebra.semirings import Semirings as Semirings, SemiringsCategory as SemiringsCategory
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.kernel.refinement import refine as refine
type Key = tuple[Hashable, ...]

@dataclass(frozen=True, eq=False)
class RingObjectData:
    carrier: CategoryOfCategories.ElementType
    addition: MorphismCategory.ObjectType
    zero: MorphismCategory.ObjectType | CategoryOfCategories.ElementType
    multiplication: MorphismCategory.ObjectType
    one: MorphismCategory.ObjectType | CategoryOfCategories.ElementType
    inversion: MorphismCategory.ObjectType

    @property
    def unit(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        ...

class RingObjectDeclaration:

    def __init__(self, data: RingObjectData) -> None:
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

    def inversion(self) -> MorphismCategory.ObjectType:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class RingMorphismData:
    carrier_morphism: MorphismCategory.ObjectType

class RingMorphismDeclaration:

    def __init__(self, data: RingMorphismData) -> None:
        ...

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
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

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def construct_morphism(self, domain: RingsCategory.ObjectType, codomain: RingsCategory.ObjectType, carrier_morphism: MorphismCategory.ObjectType) -> RingsCategory.MorphismType:
        ...

    def __call__(self, carrier: CategoryOfCategories.ElementType, addition: MorphismCategory.ObjectType, zero: MorphismCategory.ObjectType | CategoryOfCategories.ElementType, multiplication: MorphismCategory.ObjectType, one: MorphismCategory.ObjectType | CategoryOfCategories.ElementType, inversion: MorphismCategory.ObjectType) -> RingsCategory.ObjectType:
        ...

def Rings(ambient: Category) -> RingsCategory:
    ...
