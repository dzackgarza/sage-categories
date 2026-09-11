import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
import sage_categories.sets.finite
from collections.abc import Hashable
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import NN as NN, omega as omega
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.predicates import Proposition as Proposition
from sage_categories.cat.shapes import ThinCategory as ThinCategory
from sage_categories.sets.finite import MembershipRule as MembershipRule
from sage_categories.cat.declarations import Sets as Sets

def positive_integer(value: Hashable) -> Proposition:
    ...

class PositiveIntegersCategory(Category):

    class ObjectType(sage_categories.sets.finite.SetsCategory.ElementType, sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def set_presentation(self) -> MembershipRule:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

def natural_order(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> bool:
    ...

class SequentialCategory(ThinCategory):

    def __init__(self) -> None:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...
