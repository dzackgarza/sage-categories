import sage_categories.cat.morphisms
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition
__all__ = ['PointMorphismCategory', 'PointCategory']

class _PointObjectPredicate(Predicate):
    name: str

class _PointIdentityPredicate(Predicate):
    name: str

class _StaticRoles_PointMorphismCategory(sage_categories.cat.morphisms._StaticRoles_MorphismCategory):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

        def domain(self) -> PointMorphismCategory.ObjectType:
            ...

        def codomain(self) -> PointMorphismCategory.ObjectType:
            ...

class PointMorphismCategory(_StaticRoles_PointMorphismCategory, MorphismCategory[[], [], _StaticRoles_PointMorphismCategory.ObjectType, _StaticRoles_PointMorphismCategory.ElementType, _StaticRoles_PointMorphismCategory.MorphismType]):

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

class _StaticRoles_PointCategory:

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

        def domain(self) -> PointCategory.ObjectType:
            ...

        def codomain(self) -> PointCategory.ObjectType:
            ...

class PointCategory(_StaticRoles_PointCategory, Category[[], [], _StaticRoles_PointCategory.ObjectType, _StaticRoles_PointCategory.ElementType, _StaticRoles_PointCategory.MorphismType]):

    def __init__(self, member: CategoryOfCategories.ElementType) -> None:
        ...

    def member(self) -> CategoryOfCategories.ElementType:
        ...

    def structure_functors(self) -> tuple[CategoryOfCategories.MorphismType, ...]:
        ...

    def morphism_category_type(self) -> type[PointMorphismCategory]:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__(self) -> CategoryOfCategories.ElementType:
        ...

    def construct_morphism(self, domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def construct_identity(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def inverse_morphism(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...
