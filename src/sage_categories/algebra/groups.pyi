from dataclasses import dataclass
from sage_categories.algebra.monoids import Monoids as Monoids, MonoidsCategory as MonoidsCategory
from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.sets.category import Sets as Sets
from typing import Any

@dataclass(frozen=True, eq=False, slots=True)
class GroupObjectData:
    carrier: Any
    multiplication: Any
    unit: Any
    inversion: Any

class GroupObjectDeclaration:

    def __init__(self, data: Any) -> None:
        ...

    def carrier(self) -> Any:
        ...

    def multiplication(self) -> Any:
        ...

    def unit_morphism(self) -> Any:
        ...

    def inversion(self) -> Any:
        ...

    def zero(self) -> Any:
        ...

    def one(self) -> Any:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class GroupMorphismData:
    carrier_morphism: Any

class GroupMorphismDeclaration:

    def __init__(self, data: GroupMorphismData) -> None:
        ...

    def carrier_morphism(self) -> Any:
        ...

@dataclass(frozen=True, eq=False)
class GroupPresentation:
    presented_group: GroupObjectDeclaration
    generators: tuple[str, ...]
    relations: tuple[Any, ...]
    free_group_on_generators: Any
    free_group_on_relations: Any
    first_parallel_morphism: Any
    second_parallel_morphism: Any
    evaluation_morphism: Any

    def coequalizer_presentation(self) -> tuple[Any, Any, Any]:
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

    def to_monoids(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Any, ...]:
        ...

    def construct_morphism(self, domain: GroupsCategory.ObjectType, codomain: GroupsCategory.ObjectType, carrier_morphism: Any) -> GroupsCategory.MorphismType:
        ...

    def infinite_cyclic(self) -> GroupsCategory.ObjectType:
        ...

    def presentation(self, generators: tuple[str, ...], relations: tuple[Any, ...]=()) -> GroupPresentation:
        ...

    def __call__(self, carrier: Any, multiplication: Any, unit: Any, inversion: Any) -> GroupsCategory.ObjectType:
        ...

def Groups(ambient: Category | None=None) -> GroupsCategory:
    ...
