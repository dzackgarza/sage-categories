from dataclasses import dataclass
from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.predicates import Predicate as Predicate, predicate as predicate
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.sets.category import Sets as Sets
from typing import Any
preserves_module_action: Predicate

@dataclass(frozen=True, eq=False)
class ModuleObjectData:
    carrier: Any
    action_morphism: Any

class ModuleObjectDeclaration:

    def __init__(self, data: Any) -> None:
        ...

    def carrier(self) -> Any:
        ...

    def action(self) -> Any:
        ...

    def action_morphism(self) -> Any:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class ModuleMorphismData:
    carrier_morphism: Any

class ModuleMorphismDeclaration:

    def __init__(self, data: ModuleMorphismData) -> None:
        ...

    def carrier_morphism(self) -> Any:
        ...

@dataclass(frozen=True, eq=False)
class ModulePresentation:
    presented_module: ModuleObjectDeclaration
    generators_module: Any
    relations_module: Any
    matrix_morphism: Any
    presentation_morphism: Any
    rank: int
    relations_matrix: tuple[tuple[Any, ...], ...]

class ModulesCategory(Category[[], []]):
    ObjectType = ModuleObjectDeclaration
    MorphismType = ModuleMorphismDeclaration

    class ElementType:
        ...

    def __init__(self, monoid: Any, ambient: Category | None=None, action: Functor | None=None) -> None:
        ...

    def monoid(self) -> Any:
        ...

    def ambient(self) -> Category:
        ...

    def actegory_action(self) -> Functor | None:
        ...

    def Free(self) -> PropertySubcategory:
        ...

    def FiniteRank(self) -> PropertySubcategory:
        ...

    def Based(self) -> PropertySubcategory:
        ...

    def U_A(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Any, ...]:
        ...

    def construct_morphism(self, domain: ModulesCategory.ObjectType, codomain: ModulesCategory.ObjectType, carrier_morphism: Any) -> ModulesCategory.MorphismType:
        ...

    def regular(self) -> ModulesCategory.ObjectType:
        ...

    def presentation(self, relations_matrix: tuple[tuple[Any, ...], ...] | list[list[Any]]=(), rank: int=1) -> ModulePresentation:
        ...

    def from_endomorphism_action(self, A_to_End_X: Any) -> ModulesCategory.ObjectType:
        ...

    def from_sage_module(self, engine_module: Any) -> ModulesCategory.ObjectType:
        ...

    def __call__(self, rho_X: Any) -> ModulesCategory.ObjectType:
        ...

def Modules(monoid: Any, ambient: Category | None=None) -> ModulesCategory:
    ...
