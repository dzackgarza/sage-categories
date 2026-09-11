import sage_categories.cat.comma
import sage_categories.cat.properties
import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
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

class _StaticRoles_SliceLikeCategory(sage_categories.cat.comma._StaticRoles_CommaSpecialization):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> SliceLikeCategory.ObjectType:
            ...

        def codomain(self) -> SliceLikeCategory.ObjectType:
            ...

class SliceLikeCategory(_StaticRoles_SliceLikeCategory, CommaSpecialization[_StaticRoles_SliceLikeCategory.ObjectType, _StaticRoles_SliceLikeCategory.ElementType, _StaticRoles_SliceLikeCategory.MorphismType]):

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

class _StaticRoles_SliceProperty(sage_categories.cat.properties._StaticRoles_FullSubcategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> SliceProperty.ObjectType:
            ...

        def codomain(self) -> SliceProperty.ObjectType:
            ...

class SliceProperty[_ObjectRole = _StaticRoles_SliceProperty.ObjectType, _ElementRole = _StaticRoles_SliceProperty.ElementType, _MorphismRole = _StaticRoles_SliceProperty.MorphismType](_StaticRoles_SliceProperty, FullSubcategory[[MorphismCategory.ObjectType], [], _ObjectRole, _ElementRole, _MorphismRole]):

    def __init__(self, ambient: SliceLikeCategory | SliceProperty, property_category: Category) -> None:
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

class _StaticRoles_SubobjectsOfProduct(_StaticRoles_SliceProperty):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def product_projection(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> SubobjectsOfProduct.ObjectType:
            ...

        def codomain(self) -> SubobjectsOfProduct.ObjectType:
            ...

class SubobjectsOfProduct(_StaticRoles_SubobjectsOfProduct, SliceProperty[_StaticRoles_SubobjectsOfProduct.ObjectType, _StaticRoles_SubobjectsOfProduct.ElementType, _StaticRoles_SubobjectsOfProduct.MorphismType]):
    pass

def _pair_functor(first: Functor, second: Functor) -> Functor:
    ...

def _endpoint_functor(base: Category) -> Functor:
    ...

def _construct_comma_category(first: Functor, second: Functor, category_type: type[CommaCategory]=...) -> CommaCategory:
    ...
