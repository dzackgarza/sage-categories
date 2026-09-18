from collections.abc import Hashable

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
import sage_categories.sets.finite
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import NN as NN
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.declarations import omega as omega
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.predicates import Proposition as Proposition
from sage_categories.cat.shapes import ThinCategory as ThinCategory
from sage_categories.sets.finite import MembershipRule as MembershipRule

def positive_integer(value: Hashable) -> Proposition: ...

class _StaticRoles_PositiveIntegersCategory:
    class ObjectType(sage_categories.sets.finite._StaticRoles_SetsCategory.ElementType, sage_categories.kernel.roles.ObjectOfCategory): ...
    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def domain(self) -> PositiveIntegersCategory.ObjectType: ...
        def codomain(self) -> PositiveIntegersCategory.ObjectType: ...

class PositiveIntegersCategory(
    _StaticRoles_PositiveIntegersCategory,
    Category[..., ..., _StaticRoles_PositiveIntegersCategory.ObjectType, _StaticRoles_PositiveIntegersCategory.ElementType, _StaticRoles_PositiveIntegersCategory.MorphismType],
):
    def set_presentation(self) -> MembershipRule: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...

def natural_order(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> bool: ...

class SequentialCategory(ThinCategory):
    def structure_functors(self) -> tuple[Functor, ...]: ...
