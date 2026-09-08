import sage_categories
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['AdjunctionsCategory', 'EquivalencesCategory', 'Adjunctions', 'Equivalences']

@dataclass(frozen=True, eq=False, slots=True)
class AdjunctionData:
    forward: Functor
    inverse: Functor
    unit: NaturalTransformation
    counit: NaturalTransformation

@dataclass(frozen=True, eq=False, slots=True)
class AdjunctionMorphismData:
    forward: NaturalTransformation
    inverse: NaturalTransformation

@dataclass(frozen=True, eq=False, slots=True)
class EquivalenceData:
    forward: Functor
    inverse: Functor
    unit: NaturalTransformation
    counit: NaturalTransformation

@dataclass(frozen=True, eq=False, slots=True)
class EquivalenceMorphismData:
    transformation: NaturalTransformation

class AdjunctionsCategory(Category[[NaturalTransformation, NaturalTransformation], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def __init__(self, data: AdjunctionData) -> None:
            ...

        def forward(self) -> Functor:
            ...

        def inverse(self) -> Functor:
            ...

        def unit(self) -> NaturalTransformation:
            ...

        def counit(self) -> NaturalTransformation:
            ...

        def transpose(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            ...

        def untranspose(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: AdjunctionMorphismData) -> None:
            ...

        def forward_transformation(self) -> NaturalTransformation:
            ...

        def inverse_transformation(self) -> NaturalTransformation:
            ...

    def __init__(self, forward: Functor, inverse: Functor) -> None:
        ...

    def forward(self) -> Functor:
        ...

    def inverse(self) -> Functor:
        ...

    def source_category(self) -> Category:
        ...

    def target_category(self) -> Category:
        ...

    def __call__(self, unit: NaturalTransformation, counit: NaturalTransformation) -> AdjunctionsCategory.ObjectType:
        ...

    def construct_morphism(self, source: AdjunctionsCategory.ObjectType, target: AdjunctionsCategory.ObjectType, forward: NaturalTransformation, inverse: NaturalTransformation) -> AdjunctionsCategory.MorphismType:
        ...

    def construct_identity(self, member_object: AdjunctionsCategory.ObjectType) -> AdjunctionsCategory.MorphismType:
        ...

    def composite(self, second: AdjunctionsCategory.MorphismType, first: AdjunctionsCategory.MorphismType) -> AdjunctionsCategory.MorphismType:
        ...

class EquivalencesCategory(Category[[NaturalTransformation], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def __init__(self, data: EquivalenceData) -> None:
            ...

        def forward(self) -> Functor:
            ...

        def inverse(self) -> Functor:
            ...

        def unit(self) -> NaturalTransformation:
            ...

        def counit(self) -> NaturalTransformation:
            ...

        def adjunction(self) -> AdjunctionsCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: EquivalenceMorphismData) -> None:
            ...

        def transformation(self) -> NaturalTransformation:
            ...

    def __init__(self, source: Category, target: Category) -> None:
        ...

    def source_category(self) -> Category:
        ...

    def target_category(self) -> Category:
        ...

    def __call__(self, forward: Functor, inverse: Functor, unit: NaturalTransformation, counit: NaturalTransformation) -> EquivalencesCategory.ObjectType:
        ...

    def construct_morphism(self, source: EquivalencesCategory.ObjectType, target: EquivalencesCategory.ObjectType, transformation: NaturalTransformation) -> EquivalencesCategory.MorphismType:
        ...

    def construct_identity(self, member_object: EquivalencesCategory.ObjectType) -> EquivalencesCategory.MorphismType:
        ...

    def composite(self, second: EquivalencesCategory.MorphismType, first: EquivalencesCategory.MorphismType) -> EquivalencesCategory.MorphismType:
        ...

    @cached_method
    def forward_projection(self) -> Functor:
        ...

def Adjunctions(forward: Functor, inverse: Functor) -> AdjunctionsCategory:
    ...

def Equivalences(source: Category, target: Category) -> EquivalencesCategory:
    ...
