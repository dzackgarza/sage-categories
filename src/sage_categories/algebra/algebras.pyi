from collections.abc import Hashable
from dataclasses import dataclass
from sage.misc.cachefunc import cached_method
from sage_categories.algebra.modules import ModuleObjectDeclaration as ModuleObjectDeclaration, Modules as Modules, ModulesCategory as ModulesCategory
from sage_categories.algebra.monoids import MonoidObjectDeclaration as MonoidObjectDeclaration, Monoids as Monoids, MonoidsCategory as MonoidsCategory
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Predicate as Predicate, predicate as predicate
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.sets.category import Sets as Sets
type Key = tuple[Hashable, ...]
preserves_algebra_multiplication: Predicate
preserves_algebra_unit: Predicate

@dataclass(frozen=True, eq=False)
class AlgebraObjectData:
    module: ModuleObjectDeclaration
    multiplication: MorphismCategory.ObjectType
    unit: MorphismCategory.ObjectType

    @property
    def carrier(self) -> ModuleObjectDeclaration:
        ...

    @property
    def action_morphism(self) -> MorphismCategory.ObjectType:
        ...

class AlgebraObjectDeclaration:

    def __init__(self, data: AlgebraObjectData) -> None:
        ...

    def module(self) -> ModuleObjectDeclaration:
        ...

    def carrier(self) -> CategoryOfCategories.ElementType:
        ...

    def multiplication(self) -> MorphismCategory.ObjectType:
        ...

    def unit_morphism(self) -> MorphismCategory.ObjectType:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class AlgebraMorphismData:
    module_morphism: MorphismCategory.ObjectType

    @property
    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        ...

class AlgebraMorphismDeclaration:

    def __init__(self, data: AlgebraMorphismData) -> None:
        ...

    def module_morphism(self) -> MorphismCategory.ObjectType:
        ...

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        ...

@dataclass(frozen=True, eq=False)
class AlgebraPresentation:
    presented_algebra: AlgebraObjectDeclaration
    generators: tuple[str, ...]
    relations: tuple[str, ...]
    free_algebra_on_generators: AlgebraObjectDeclaration
    evaluation_morphism: MorphismCategory.ObjectType

class AlgebrasCategory(Category[[], []]):
    ObjectType = AlgebraObjectDeclaration
    MorphismType = AlgebraMorphismDeclaration

    class ElementType:
        ...

    def __init__(self, base: MonoidObjectDeclaration, ambient: Category) -> None:
        ...

    def base(self) -> MonoidObjectDeclaration:
        ...

    def ambient(self) -> Category:
        ...

    def module_category(self) -> ModulesCategory:
        ...

    def Commutative(self) -> PropertySubcategory:
        ...

    @cached_method
    def monoid_presentation(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    @cached_method
    def U_R(self) -> Functor:
        ...

    def construct_morphism(self, domain: AlgebrasCategory.ObjectType, codomain: AlgebrasCategory.ObjectType, module_morphism: MorphismCategory.ObjectType) -> AlgebrasCategory.MorphismType:
        ...

    def presentation(self, generators: tuple[str, ...], relations: tuple[str, ...]) -> AlgebraPresentation:
        ...

    def __call__(self, module: ModuleObjectDeclaration, multiplication: MorphismCategory.ObjectType, unit: MorphismCategory.ObjectType) -> AlgebrasCategory.ObjectType:
        ...

def Algebras(base: MonoidObjectDeclaration, ambient: Category) -> AlgebrasCategory:
    ...
