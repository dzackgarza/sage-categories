from collections.abc import Hashable
from dataclasses import dataclass
from sage.misc.cachefunc import cached_method
from sage_categories.algebra.monoids import MonoidObjectData as MonoidObjectData, Monoids as Monoids, MonoidsCategory as MonoidsCategory
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.sets.category import Sets as Sets
type Key = tuple[Hashable, ...]

@dataclass(frozen=True, eq=False, slots=True)
class GroupObjectData(MonoidObjectData):
    inversion: MorphismCategory.ObjectType

class GroupObjectDeclaration:

    def __init__(self, data: GroupObjectData) -> None:
        ...

    def carrier(self) -> CategoryOfCategories.ElementType:
        ...

    def multiplication(self) -> MorphismCategory.ObjectType:
        ...

    def unit_morphism(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        ...

    def inversion(self) -> MorphismCategory.ObjectType:
        ...

    def zero(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        ...

    def one(self) -> MorphismCategory.ObjectType | CategoryOfCategories.ElementType:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class GroupMorphismData:
    carrier_morphism: MorphismCategory.ObjectType

class GroupMorphismDeclaration:

    def __init__(self, data: GroupMorphismData) -> None:
        ...

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        ...

@dataclass(frozen=True, eq=False)
class GroupPresentation:
    presented_group: GroupObjectDeclaration
    generators: tuple[str, ...]
    relations: tuple[str, ...]
    free_group_on_generators: GroupObjectDeclaration
    free_group_on_relations: GroupObjectDeclaration
    first_parallel_morphism: MorphismCategory.ObjectType
    second_parallel_morphism: MorphismCategory.ObjectType
    evaluation_morphism: MorphismCategory.ObjectType

    def coequalizer_presentation(self) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
        ...

class GroupsCategory(Category[[], []]):
    ObjectType = GroupObjectDeclaration
    MorphismType = GroupMorphismDeclaration

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

    @cached_method
    def to_monoids(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def construct_morphism(self, domain: GroupsCategory.ObjectType, codomain: GroupsCategory.ObjectType, carrier_morphism: MorphismCategory.ObjectType) -> GroupsCategory.MorphismType:
        ...

    def infinite_cyclic(self) -> GroupsCategory.ObjectType:
        ...

    def presentation(self, generators: tuple[str, ...], relations: tuple[str, ...]) -> GroupPresentation:
        ...

    def __call__(self, carrier: CategoryOfCategories.ElementType, multiplication: MorphismCategory.ObjectType, unit: MorphismCategory.ObjectType | CategoryOfCategories.ElementType, inversion: MorphismCategory.ObjectType) -> GroupsCategory.ObjectType:
        ...

def Groups(ambient: Category) -> GroupsCategory:
    ...
