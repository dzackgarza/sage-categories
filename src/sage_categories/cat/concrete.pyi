import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.cat.properties
import sage_categories.kernel.roles
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryDeclaration as CategoryDeclaration
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.category import concrete_category as concrete_category
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.predicates import Proposition as Proposition
from sage_categories.cat.predicates import register_handler as register_handler
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.kernel.sage_runtime import cached_method as cached_method

__all__ = ["ConcreteCategory"]

class _StaticRoles_ConcreteCategory(sage_categories.cat.properties._StaticRoles_PropertySubcategory):
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        @cached_method
        def functor_to_sets(self) -> Functor: ...
        def underlying_set(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType: ...
        def underlying_map(self, arrow: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def domain(self) -> ConcreteCategory.ObjectType: ...
        def codomain(self) -> ConcreteCategory.ObjectType: ...

class ConcreteCategory(
    _StaticRoles_ConcreteCategory,
    PropertySubcategory[..., ..., _StaticRoles_ConcreteCategory.ObjectType, _StaticRoles_ConcreteCategory.ElementType, _StaticRoles_ConcreteCategory.MorphismType],
): ...
