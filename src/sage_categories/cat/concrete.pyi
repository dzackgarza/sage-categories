import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['ConcreteCategory']

class ConcreteCategory(PropertySubcategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        @cached_method
        def functor_to_sets(self) -> Functor:
            ...

        def underlying_set(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

        def underlying_map(self, arrow: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> ConcreteCategory.ObjectType:
            ...

        def codomain(self) -> ConcreteCategory.ObjectType:
            ...
