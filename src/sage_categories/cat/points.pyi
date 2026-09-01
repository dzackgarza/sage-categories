from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Proposition
__all__ = ['PointMorphismCategory', 'PointCategory']

class PointMorphismCategory(MorphismCategory[[], []]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

class PointCategory(Category[[], []]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

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
