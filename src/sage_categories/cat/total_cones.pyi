from _typeshed import Incomplete

import sage_categories.cat.category
import sage_categories.cat.comma
import sage_categories.cat.morphisms
import sage_categories.cat.properties
import sage_categories.kernel.roles
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.comma import CommaSpecialization as CommaSpecialization
from sage_categories.cat.cones import ConeCategory as ConeCategory
from sage_categories.cat.cones import cones as cones
from sage_categories.cat.cones import limit_cones as limit_cones
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import FunctorCategory as FunctorCategory
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Axiom as Axiom
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.kernel.refinement import is_placed as is_placed
from sage_categories.kernel.refinement import refine as refine
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = ["TotalConesCategory", "TotalLimitConesCategory", "total_cones"]

class _StaticRoles_TotalConesCategory(sage_categories.cat.comma._StaticRoles_CommaSpecialization):
    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def presentation(self) -> ConeCategory.ObjectType: ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        def apex_morphism(self) -> MorphismCategory.ObjectType: ...
        def diagram_transformation(self) -> NaturalTransformation: ...
        def domain(self) -> TotalConesCategory.ObjectType: ...
        def codomain(self) -> TotalConesCategory.ObjectType: ...

class TotalConesCategory(
    _StaticRoles_TotalConesCategory,
    CommaSpecialization[_StaticRoles_TotalConesCategory.ObjectType, _StaticRoles_TotalConesCategory.ElementType, _StaticRoles_TotalConesCategory.MorphismType],
):
    LimitCones: Incomplete

    def diagrams(self) -> FunctorCategory: ...
    def diagonal_functor(self) -> Functor: ...
    def identity_functor(self) -> Functor: ...
    def diagram_projection(self) -> Functor: ...
    def apex_functor(self) -> Functor: ...
    def apex_fiber(self, apex: CategoryOfCategories.ElementType) -> Category: ...
    def __call__(self, presentation: ConeCategory.ObjectType) -> TotalConesCategory.ObjectType: ...

class _StaticRoles_TotalLimitConesCategory(sage_categories.cat.properties._StaticRoles_PropertySubcategory):
    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory): ...
    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> TotalLimitConesCategory.ObjectType: ...
        def codomain(self) -> TotalLimitConesCategory.ObjectType: ...

class TotalLimitConesCategory(
    _StaticRoles_TotalLimitConesCategory,
    PropertySubcategory[
        [MorphismCategory.ObjectType, NaturalTransformation],
        [],
        _StaticRoles_TotalLimitConesCategory.ObjectType,
        _StaticRoles_TotalLimitConesCategory.ElementType,
        _StaticRoles_TotalLimitConesCategory.MorphismType,
    ],
):
    pass

def total_cones(diagrams: FunctorCategory) -> TotalConesCategory: ...
