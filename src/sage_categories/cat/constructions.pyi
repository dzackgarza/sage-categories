import sage_categories
from collections.abc import Callable, Hashable
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory, cocone as cocone, cocone_apex as cocone_apex, cone as cone, cone_apex as cone_apex, vertex_of as vertex_of
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import FullSubcategory, PredicateSubcategory
__all__ = ['cocone', 'cocone_apex', 'cone', 'cone_apex', 'vertex_of', 'presenting_family', 'ApexCategory', 'LimitsCategory', 'ProductsCategory', 'ColimitsCategory', 'CoproductsCategory', 'limits', 'colimits']
type Mediator = Callable[[NaturalTransformation], MorphismCategory.ObjectType]
type Construction = Callable[[Functor], 'CategoryOfCategories.ElementType']
type UniversalPresentation = LimitConesCategory.ObjectType

def presenting_family(constructed: CategoryOfCategories.ElementType) -> Category:
    ...

class ApexCategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData]) -> None:
        ...

    def accepts(self, diagram: Functor, shape: Category) -> None:
        ...

    def lowered(self, diagram: Functor) -> Functor:
        ...

    def has_construction(self, diagram: Functor) -> bool:
        ...

    def chosen_object(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        ...

    def universal_data(self, diagram: Functor) -> UniversalPresentation:
        ...

    def presenting_diagrams(self, constructed: CategoryOfCategories.ElementType) -> tuple[Functor, ...]:
        ...

    def presentation(self, constructed: CategoryOfCategories.ElementType) -> UniversalPresentation:
        ...

    def chosen(self, diagram: Functor, construction: Construction) -> CategoryOfCategories.ElementType:
        ...

class LimitsCategory(ApexCategory):

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.category.CategoryOfCategories.MorphismType, sage_categories.kernel.roles.MorphismOfCategory):
        ...

    class ObjectType(sage_categories.cat.category.CategoryDeclaration, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    def __init__(self, ambient: Category, shape: Category) -> None:
        ...

    def shape(self) -> Category:
        ...

    def diagrams(self) -> Category:
        ...

    def __call__(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        ...

    def with_universal_data(self, diagram: Functor, apex: CategoryOfCategories.ElementType, limiting_cone: NaturalTransformation, mediator: Mediator) -> CategoryOfCategories.ElementType:
        ...

    def limit_functor(self) -> Functor:
        ...

    def defining_functor(self) -> Functor:
        ...

    def factorization(self) -> tuple[Functor, Functor]:
        ...

    def adjunction(self) -> CategoryOfCategories.ElementType:
        ...

    def name(self) -> str:
        ...

class ProductsCategory(PredicateSubcategory[[MorphismCategory.ObjectType], []]):

    class ElementType:
        ...

    class MorphismType:
        ...

    class ObjectType:

        def product_factors(self) -> Functor:
            ...

        def index_category(self) -> Category:
            ...

        def cone(self) -> NaturalTransformation:
            ...

        def product_projection(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            ...

        def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismCategory.ObjectType:
            ...

    def __init__(self, ambient: Category) -> None:
        ...

    def retain_full_image(self, family: Category) -> None:
        ...

    def full_images(self) -> tuple[Category, ...]:
        ...

    def retain_product(self, family: Category, apex: CategoryOfCategories.ElementType) -> None:
        ...

    def presenting_family(self, apex: CategoryOfCategories.ElementType) -> Category:
        ...

    def diagrams(self, shape: Category) -> Category:
        ...

    def __call__(self, family: Functor | tuple[CategoryOfCategories.ElementType, ...]) -> CategoryOfCategories.ElementType:
        ...

    def with_universal_data(self, diagram: Functor, apex: CategoryOfCategories.ElementType, limiting_cone: NaturalTransformation, mediator: Mediator) -> CategoryOfCategories.ElementType:
        ...

    def name(self) -> str:
        ...

class ColimitsCategory(FullSubcategory[[MorphismCategory.ObjectType], []]):

    class ElementType:
        ...

    class MorphismType:
        ...

    class ObjectType:

        def diagram(self) -> Functor:
            ...

        def index_category(self) -> Category:
            ...

        def cocone(self) -> NaturalTransformation:
            ...

        def injection(self, index: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            ...

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismCategory.ObjectType:
            ...

    def __init__(self, ambient: Category, shape: Category) -> None:
        ...

    def shape(self) -> Category:
        ...

    def diagrams(self) -> Category:
        ...

    def accepts(self, diagram: Functor) -> None:
        ...

    def lowered(self, diagram: Functor) -> Functor:
        ...

    def has_construction(self, diagram: Functor) -> bool:
        ...

    def chosen_object(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        ...

    def universal_data(self, diagram: Functor) -> UniversalPresentation:
        ...

    def presenting_diagrams(self, constructed: CategoryOfCategories.ElementType) -> tuple[Functor, ...]:
        ...

    def presenting_diagram(self, constructed: CategoryOfCategories.ElementType) -> Functor:
        ...

    def presentation(self, constructed: CategoryOfCategories.ElementType) -> UniversalPresentation:
        ...

    def __call__(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        ...

    def with_universal_data(self, diagram: Functor, apex: CategoryOfCategories.ElementType, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> CategoryOfCategories.ElementType:
        ...

    def colimit_functor(self) -> Functor:
        ...

    def defining_functor(self) -> Functor:
        ...

    def name(self) -> str:
        ...

class CoproductsCategory(PredicateSubcategory[[MorphismCategory.ObjectType], []]):

    class ElementType:
        ...

    class MorphismType:
        ...

    class ObjectType:

        def coproduct_summands(self) -> Functor:
            ...

        def coproduct_injection(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            ...

    def __init__(self, ambient: Category) -> None:
        ...

    def retain_full_image(self, family: Category) -> None:
        ...

    def full_images(self) -> tuple[Category, ...]:
        ...

    def retain_coproduct(self, family: Category, apex: CategoryOfCategories.ElementType) -> None:
        ...

    def presenting_family(self, apex: CategoryOfCategories.ElementType) -> ColimitsCategory:
        ...

    def diagrams(self, shape: Category) -> Category:
        ...

    def __call__(self, family: Functor | tuple[CategoryOfCategories.ElementType, ...]) -> CategoryOfCategories.ElementType:
        ...

    def with_universal_data(self, diagram: Functor, apex: CategoryOfCategories.ElementType, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> CategoryOfCategories.ElementType:
        ...

    def name(self) -> str:
        ...

def limits(ambient: Category, shape: Category) -> Category:
    ...

def colimits(ambient: Category, shape: Category) -> Category:
    ...
