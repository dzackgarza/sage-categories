import sage_categories.cat.comma
import sage_categories.cat.properties
import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from _typeshed import Incomplete
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.comma import CommaSpecialization
from sage_categories.cat.cones import ConeCategory
from sage_categories.cat.functors import Functor, FunctorCategory, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import PropertySubcategory
__all__ = ['TotalConesCategory', 'TotalLimitConesCategory', 'total_cones']

class _StaticRoles_TotalConesCategory(sage_categories.cat.comma._StaticRoles_CommaSpecialization):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def presentation(self) -> ConeCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def apex_morphism(self) -> MorphismCategory.ObjectType:
            ...

        def diagram_transformation(self) -> NaturalTransformation:
            ...

        def domain(self) -> TotalConesCategory.ObjectType:
            ...

        def codomain(self) -> TotalConesCategory.ObjectType:
            ...

class TotalConesCategory(_StaticRoles_TotalConesCategory, CommaSpecialization[_StaticRoles_TotalConesCategory.ObjectType, _StaticRoles_TotalConesCategory.ElementType, _StaticRoles_TotalConesCategory.MorphismType]):
    LimitCones: Incomplete

    def diagrams(self) -> FunctorCategory:
        ...

    def diagonal_functor(self) -> Functor:
        ...

    def identity_functor(self) -> Functor:
        ...

    def diagram_projection(self) -> Functor:
        ...

    def apex_functor(self) -> Functor:
        ...

    def apex_fiber(self, apex: CategoryOfCategories.ElementType) -> Category:
        ...

    def __call__(self, presentation: ConeCategory.ObjectType) -> TotalConesCategory.ObjectType:
        ...

class _StaticRoles_TotalLimitConesCategory(sage_categories.cat.properties._StaticRoles_PropertySubcategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> TotalLimitConesCategory.ObjectType:
            ...

        def codomain(self) -> TotalLimitConesCategory.ObjectType:
            ...

class TotalLimitConesCategory(_StaticRoles_TotalLimitConesCategory, PropertySubcategory[[MorphismCategory.ObjectType, NaturalTransformation], [], _StaticRoles_TotalLimitConesCategory.ObjectType, _StaticRoles_TotalLimitConesCategory.ElementType, _StaticRoles_TotalLimitConesCategory.MorphismType]):
    pass

def total_cones(diagrams: FunctorCategory) -> TotalConesCategory:
    ...
