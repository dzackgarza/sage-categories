from dataclasses import dataclass
from sage_categories.algebra.modules import Modules as Modules, ModulesCategory as ModulesCategory
from sage_categories.algebra.monoids import Monoids as Monoids
from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.predicates import Predicate as Predicate, predicate as predicate
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.sets.category import Sets as Sets
from typing import Any
preserves_algebra_multiplication: Predicate
preserves_algebra_unit: Predicate

@dataclass(frozen=True, eq=False)
class AlgebraObjectData:
    module: Any
    multiplication: Any
    unit: Any

    @property
    def carrier(self) -> Any:
        ...

class AlgebraObjectDeclaration:

    def __init__(self, data: Any) -> None:
        ...

    def module(self) -> Any:
        ...

    def carrier(self) -> Any:
        ...

    def multiplication(self) -> Any:
        ...

    def unit_morphism(self) -> Any:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class AlgebraMorphismData:
    module_morphism: Any

    @property
    def carrier_morphism(self) -> Any:
        ...

class AlgebraMorphismDeclaration:

    def __init__(self, data: Any) -> None:
        ...

    def module_morphism(self) -> Any:
        ...

    def carrier_morphism(self) -> Any:
        ...

@dataclass(frozen=True, eq=False)
class AlgebraPresentation:
    presented_algebra: AlgebraObjectDeclaration
    generators: tuple[str, ...]
    relations: tuple[Any, ...]
    free_algebra_on_generators: Any
    evaluation_morphism: Any

class AlgebrasCategory(Category[[], []]):
    ObjectType = AlgebraObjectDeclaration
    MorphismType = AlgebraMorphismDeclaration

    class ElementType:
        ...

    def __init__(self, base: Any, ambient: Category | None=None, module_category: ModulesCategory | None=None) -> None:
        ...

    def base(self) -> Any:
        ...

    def ambient(self) -> Category:
        ...

    def module_category(self) -> ModulesCategory:
        ...

    def Commutative(self) -> PropertySubcategory:
        ...

    def monoid_presentation(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Any, ...]:
        ...

    def U_R(self) -> Functor:
        ...

    def construct_morphism(self, domain: AlgebrasCategory.ObjectType, codomain: AlgebrasCategory.ObjectType, module_morphism: Any) -> AlgebrasCategory.MorphismType:
        ...

    def presentation(self, generators: tuple[str, ...], relations: tuple[Any, ...]=()) -> AlgebraPresentation:
        ...

    def __call__(self, module: Any, multiplication: Any=None, unit: Any=None) -> AlgebrasCategory.ObjectType:
        ...

def Algebras(base: Any, ambient: Category | None=None) -> AlgebrasCategory:
    ...
