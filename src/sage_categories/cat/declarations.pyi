import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Functor as Functor

__all__ = [
    "NN",
    "ZZ",
    "CategoryFamily",
    "DeclaredCategory",
    "Groupoids",
    "MagmaObjects",
    "MonoidObjects",
    "Posets",
    "RingObjects",
    "SemiringObjects",
    "Sets",
    "TotallyOrderedSets",
    "omega",
]

class _StaticRoles_DeclaredCategory:
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory): ...
    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def domain(self) -> DeclaredCategory.ObjectType: ...
        def codomain(self) -> DeclaredCategory.ObjectType: ...

class DeclaredCategory(
    _StaticRoles_DeclaredCategory,
    Category[[], [], _StaticRoles_DeclaredCategory.ObjectType, _StaticRoles_DeclaredCategory.ElementType, _StaticRoles_DeclaredCategory.MorphismType],
):
    def __init__(self, name: str) -> None: ...
    def name(self) -> str: ...

class CategoryFamily:
    def __init__(self, name: str, domain: Category) -> None: ...
    def name(self) -> str: ...
    def domain(self) -> Category: ...
    def implemented_by(self, implementation: Functor) -> None: ...
    def __call__(self, argument: CategoryOfCategories.ElementType) -> Category: ...

Sets: Category
Posets: Category
Groupoids: Category
TotallyOrderedSets: Category
NN: Category
ZZ: Category
omega: Category
MagmaObjects: CategoryFamily
MonoidObjects: CategoryFamily
SemiringObjects: CategoryFamily
RingObjects: CategoryFamily
