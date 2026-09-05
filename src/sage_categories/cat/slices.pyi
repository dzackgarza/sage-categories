import sage_categories
from collections.abc import Hashable
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.comma import CommaCategory as CommaCategory, CommaSpecialization
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition
from sage_categories.cat.properties import FullSubcategory
__all__ = ['CommaCategory', 'SliceLikeCategory', 'slice_over', 'coslice_under', 'comma_category', 'SliceProperty', 'SubobjectsOfProduct']

class _SliceMemberPredicate(Predicate):
    name: str

class SliceLikeCategory(CommaSpecialization):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __init__(self, base: Category, fixed: CategoryOfCategories.ElementType, fixed_label: int) -> None:
        ...

    def arrows(self) -> Category:
        ...

    def fixed_evaluation(self) -> Functor:
        ...

    def defining_arrow(self) -> Functor:
        ...

    def fixed_projection(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def retain_lifts(self) -> None:
        ...

    def base_of_slice(self) -> Category:
        ...

    def fixed_object(self) -> CategoryOfCategories.ElementType:
        ...

    def fixed_end(self, morphism: MorphismCategory.ObjectType) -> CategoryOfCategories.ElementType:
        ...

    def varying_end(self, morphism: MorphismCategory.ObjectType) -> CategoryOfCategories.ElementType:
        ...

    def defining_arrow_of(self, candidate: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def property_type(self, property_category: Category) -> type[SliceProperty]:
        ...

    def Monomorphisms(self) -> Category:
        ...

    def Epimorphisms(self) -> Category:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__(self, value: CategoryOfCategories.ElementType) -> SliceLikeCategory.ObjectType:
        ...

    def construct_morphism(self, domain: SliceLikeCategory.ObjectType, codomain: SliceLikeCategory.ObjectType, varying: MorphismCategory.ObjectType) -> SliceLikeCategory.MorphismType:
        ...

    def varying_component(self, square: NaturalTransformation) -> MorphismCategory.ObjectType:
        ...

def slice_over(base: Category, fixed: CategoryOfCategories.ElementType) -> SliceLikeCategory:
    ...

def coslice_under(base: Category, fixed: CategoryOfCategories.ElementType) -> SliceLikeCategory:
    ...

def comma_category(first: Functor, second: Functor) -> CommaCategory:
    ...

class _HasMorphismPropertyPredicate(Predicate):
    name: str

class SliceProperty(FullSubcategory[[MorphismCategory.ObjectType], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __init__(self, ambient: SliceLikeCategory, property_category: Category) -> None:
        ...

    def property_category(self) -> Category:
        ...

    def base_of_slice(self) -> Category:
        ...

    def subcategory_monomorphism(self) -> Functor:
        ...

    def defining_arrow(self) -> Functor:
        ...

    def defining_arrow_of(self, candidate: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__(self, value: CategoryOfCategories.ElementType) -> SliceLikeCategory.ObjectType:
        ...

class SubobjectsOfProduct(SliceProperty):

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def product_projection(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            ...
