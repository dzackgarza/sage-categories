import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from collections.abc import Callable
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Proposition
from sage_categories.engines.diagrams import DiagramBox
from typing import NamedTuple
__all__ = ['register_cartesian_comparisons', 'MonoidalStructuresCategory', 'MonoidalStructures', 'Cartesian', 'Reversed', 'Composition', 'ActionsCategory', 'Actions', 'SelfAction', 'TrivialAction']
type CartesianComparisonHandler = Callable[..., MorphismCategory.ObjectType]

def register_cartesian_comparisons(category_type: type[Category], handler: CartesianComparisonHandler) -> None:
    ...

class _MonoidalData(NamedTuple):
    tensor: Functor
    unit: CategoryOfCategories.ElementType
    associator: NaturalTransformation
    left_unitor: NaturalTransformation
    right_unitor: NaturalTransformation

class MonoidalStructuresCategory(Category[[], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: _MonoidalData) -> None:
            ...

        def underlying_category(self) -> Category:
            ...

        def tensor(self) -> Functor:
            ...

        def unit(self) -> CategoryOfCategories.ElementType:
            ...

        def associator(self) -> NaturalTransformation:
            ...

        def left_unitor(self) -> NaturalTransformation:
            ...

        def right_unitor(self) -> NaturalTransformation:
            ...

        def diagram_wire(self, value: CategoryOfCategories.ElementType):
            ...

        def diagram_box(self, name: str, domain: tuple[CategoryOfCategories.ElementType, ...], codomain: tuple[CategoryOfCategories.ElementType, ...], arrow: MorphismCategory.ObjectType) -> DiagramBox:
            ...

        def interpret(self, diagram) -> MorphismCategory.ObjectType:
            ...

        def pentagon(self, w: CategoryOfCategories.ElementType, x: CategoryOfCategories.ElementType, y: CategoryOfCategories.ElementType, z: CategoryOfCategories.ElementType) -> Proposition:
            ...

        def triangle(self, x: CategoryOfCategories.ElementType, y: CategoryOfCategories.ElementType) -> Proposition:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __init__(self, base: Category) -> None:
        ...

    def __call__(self, tensor: Functor, unit: CategoryOfCategories.ElementType, associator: NaturalTransformation, left_unitor: NaturalTransformation, right_unitor: NaturalTransformation) -> MonoidalStructuresCategory.ObjectType:
        ...

    def construct_morphism(self, source: MonoidalStructuresCategory.ObjectType, target: MonoidalStructuresCategory.ObjectType) -> MonoidalStructuresCategory.MorphismType:
        ...

def MonoidalStructures(base: Category) -> MonoidalStructuresCategory:
    ...

def Cartesian(base: Category) -> MonoidalStructuresCategory.ObjectType:
    ...

def Reversed(monoidal: MonoidalStructuresCategory.ObjectType) -> MonoidalStructuresCategory.ObjectType:
    ...

def Composition(base: Category) -> MonoidalStructuresCategory.ObjectType:
    ...

class _ActionData(NamedTuple):
    action: Functor
    associator: NaturalTransformation
    unitor: NaturalTransformation

class ActionsCategory(Category[[], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def __init__(self, data: _ActionData) -> None:
            ...

        def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType:
            ...

        def underlying_category(self) -> Category:
            ...

        def action(self) -> Functor:
            ...

        def associator(self) -> NaturalTransformation:
            ...

        def unitor(self) -> NaturalTransformation:
            ...

        def pentagon(self, m: CategoryOfCategories.ElementType, n: CategoryOfCategories.ElementType, p: CategoryOfCategories.ElementType, x: CategoryOfCategories.ElementType) -> Proposition:
            ...

        def triangle(self, m: CategoryOfCategories.ElementType, x: CategoryOfCategories.ElementType) -> Proposition:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __init__(self, monoidal: MonoidalStructuresCategory.ObjectType, base: Category) -> None:
        ...

    def __call__(self, action: Functor, associator: NaturalTransformation, unitor: NaturalTransformation) -> ActionsCategory.ObjectType:
        ...

    def construct_morphism(self, source: ActionsCategory.ObjectType, target: ActionsCategory.ObjectType) -> ActionsCategory.MorphismType:
        ...

def Actions(monoidal: MonoidalStructuresCategory.ObjectType, base: Category) -> ActionsCategory:
    ...

def SelfAction(monoidal: MonoidalStructuresCategory.ObjectType) -> ActionsCategory.ObjectType:
    ...

def TrivialAction(monoidal: MonoidalStructuresCategory.ObjectType, base: Category) -> ActionsCategory.ObjectType:
    ...
