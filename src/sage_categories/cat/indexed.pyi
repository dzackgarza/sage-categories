import sage_categories
from collections.abc import Callable
from dataclasses import dataclass
from sage_categories.cat.adjunctions import EquivalencesCategory
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
__all__ = ['IndexedCategoriesCategory', 'GrothendieckCategory', 'IndexedCategories', 'Grothendieck']
type FiberRule = Callable[[CategoryOfCategories.ElementType], Category]
type ReindexingRule = Callable[[MorphismCategory.ObjectType], Functor]
type UnitRule = Callable[[CategoryOfCategories.ElementType], NaturalTransformation]
type CompositionRule = Callable[[MorphismCategory.ObjectType, MorphismCategory.ObjectType], NaturalTransformation]
type ComponentRule = Callable[[CategoryOfCategories.ElementType], Functor]
type ComparisonRule = Callable[[MorphismCategory.ObjectType], NaturalTransformation]

@dataclass(frozen=True, eq=False, slots=True)
class _IndexedData:
    fibers: FiberRule
    reindexing: ReindexingRule
    unit: UnitRule
    composition: CompositionRule

@dataclass(frozen=True, eq=False, slots=True)
class _IndexedTransformationData:
    components: ComponentRule
    comparisons: ComparisonRule

class IndexedCategoriesCategory(Category[[ComponentRule, ComparisonRule], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def __init__(self, data: _IndexedData) -> None:
            ...

        def domain(self) -> Category:
            ...

        def codomain(self) -> Category:
            ...

        def on_object(self, value: CategoryOfCategories.ElementType) -> Category:
            ...

        def reindex(self, morphism: MorphismCategory.ObjectType) -> Functor:
            ...

        def on_morphism(self, morphism: MorphismCategory.ObjectType) -> Functor:
            ...

        def unit(self, value: CategoryOfCategories.ElementType) -> NaturalTransformation:
            ...

        def compositor(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> NaturalTransformation:
            ...

        def total_category(self) -> GrothendieckCategory:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: _IndexedTransformationData) -> None:
            ...

        def component(self, value: CategoryOfCategories.ElementType) -> Functor:
            ...

        def comparison(self, morphism: MorphismCategory.ObjectType) -> NaturalTransformation:
            ...

        def induced_functor(self) -> Functor:
            ...

    def __init__(self, base: Category) -> None:
        ...

    def base(self) -> Category:
        ...

    def __call__(self, fibers: FiberRule, reindexing: ReindexingRule, unit: UnitRule, composition: CompositionRule) -> IndexedCategoriesCategory.ObjectType:
        ...

    def strict(self, functor: Functor) -> IndexedCategoriesCategory.ObjectType:
        ...

    def construct_morphism(self, source: IndexedCategoriesCategory.ObjectType, target: IndexedCategoriesCategory.ObjectType, components: ComponentRule, comparisons: ComparisonRule) -> IndexedCategoriesCategory.MorphismType:
        ...

    def construct_identity(self, value: IndexedCategoriesCategory.ObjectType) -> IndexedCategoriesCategory.MorphismType:
        ...

    def composite(self, second: IndexedCategoriesCategory.MorphismType, first: IndexedCategoriesCategory.MorphismType) -> IndexedCategoriesCategory.MorphismType:
        ...

    def grothendieck_functor(self) -> Functor:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class _TotalObject:
    base: CategoryOfCategories.ElementType
    fiber: CategoryOfCategories.ElementType

@dataclass(frozen=True, eq=False, slots=True)
class _TotalMorphism:
    base: MorphismCategory.ObjectType
    fiber: MorphismCategory.ObjectType

class GrothendieckCategory(Category[[MorphismCategory.ObjectType, MorphismCategory.ObjectType], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def __init__(self, data: _TotalObject) -> None:
            ...

        def base_object(self) -> CategoryOfCategories.ElementType:
            ...

        def fiber_object(self) -> CategoryOfCategories.ElementType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: _TotalMorphism) -> None:
            ...

        def base_morphism(self) -> MorphismCategory.ObjectType:
            ...

        def fiber_morphism(self) -> MorphismCategory.ObjectType:
            ...

    def __init__(self, indexed: IndexedCategoriesCategory.ObjectType) -> None:
        ...

    def indexed_category(self) -> IndexedCategoriesCategory.ObjectType:
        ...

    def __call__(self, base: CategoryOfCategories.ElementType, fiber: CategoryOfCategories.ElementType) -> GrothendieckCategory.ObjectType:
        ...

    def construct_morphism(self, source: GrothendieckCategory.ObjectType, target: GrothendieckCategory.ObjectType, base: MorphismCategory.ObjectType, fiber: MorphismCategory.ObjectType) -> GrothendieckCategory.MorphismType:
        ...

    def construct_identity(self, value: GrothendieckCategory.ObjectType) -> GrothendieckCategory.MorphismType:
        ...

    def composite(self, second: GrothendieckCategory.MorphismType, first: GrothendieckCategory.MorphismType) -> GrothendieckCategory.MorphismType:
        ...

    def projection(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def factor_cartesian(self, lift: GrothendieckCategory.MorphismType, arrow: GrothendieckCategory.MorphismType, base: MorphismCategory.ObjectType) -> GrothendieckCategory.MorphismType:
        ...

    def fiber_equivalence(self, base: CategoryOfCategories.ElementType) -> EquivalencesCategory.ObjectType:
        ...

def IndexedCategories(base: Category) -> IndexedCategoriesCategory:
    ...

def Grothendieck(indexed: IndexedCategoriesCategory.ObjectType) -> GrothendieckCategory:
    ...
