from dataclasses import dataclass
from sage.rings.integer import Integer
from sage_categories.algebra.monoids import MonoidObjectDeclaration as MonoidObjectDeclaration
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Predicate as Predicate, predicate as predicate
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.kernel.roles import Role as Role, role_of as role_of
from sage_categories.sets.category import Sets as Sets
from sage_categories.sets.elements import Datum as Datum
preserves_module_action: Predicate

@dataclass(frozen=True, eq=False)
class ModuleObjectData:
    carrier: CategoryOfCategories.ElementType
    action_morphism: MorphismCategory.ObjectType

class ModuleObjectDeclaration:

    def __init__(self, data: ModuleObjectData) -> None:
        ...

    def carrier(self) -> CategoryOfCategories.ElementType:
        ...

    def action(self) -> MorphismCategory.ObjectType:
        ...

    def action_morphism(self) -> MorphismCategory.ObjectType:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class ModuleMorphismData:
    carrier_morphism: MorphismCategory.ObjectType

class ModuleMorphismDeclaration:

    def __init__(self, data: ModuleMorphismData) -> None:
        ...

    def carrier_morphism(self) -> MorphismCategory.ObjectType:
        ...

@dataclass(frozen=True, eq=False)
class ModulePresentation:
    presented_module: ModuleObjectDeclaration
    generators_module: ModuleObjectDeclaration
    relations_module: ModuleObjectDeclaration
    matrix_morphism: MorphismCategory.ObjectType
    presentation_morphism: MorphismCategory.ObjectType
    rank: int
    relations_matrix: tuple[tuple[Datum, ...], ...]

class ModulesCategory(Category[[], []]):
    ObjectType = ModuleObjectDeclaration
    MorphismType = ModuleMorphismDeclaration

    class ElementType:
        ...

    def __init__(self, monoid: MonoidObjectDeclaration, ambient: Category) -> None:
        ...

    def monoid(self) -> MonoidObjectDeclaration:
        ...

    def ambient(self) -> Category:
        ...

    def Free(self) -> PropertySubcategory:
        ...

    def FiniteRank(self) -> PropertySubcategory:
        ...

    def Based(self) -> PropertySubcategory:
        ...

    def U_A(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def construct_morphism(self, domain: ModulesCategory.ObjectType, codomain: ModulesCategory.ObjectType, carrier_morphism: MorphismCategory.ObjectType) -> ModulesCategory.MorphismType:
        ...

    def regular(self) -> ModulesCategory.ObjectType:
        ...

    def presentation(self, relations_matrix: tuple[tuple[Datum, ...], ...], rank: int | Integer) -> ModulePresentation:
        ...

    def __call__(self, rho_X: MorphismCategory.ObjectType | ModuleObjectDeclaration) -> ModulesCategory.ObjectType:
        ...

def Modules(monoid: MonoidObjectDeclaration, ambient: Category) -> ModulesCategory:
    ...
