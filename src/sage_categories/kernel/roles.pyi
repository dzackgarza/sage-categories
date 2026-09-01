from collections.abc import Iterator
from contextlib import contextmanager
from enum import Enum
from sage_categories.cat.category import Category
from sage_categories.cat.predicates import AppliedPredicate, Proposition
__all__ = ['Role', 'building_role_classes', 'CategoryPoint', 'ObjectOfCategory', 'ElementOfObject', 'MorphismOfCategory', 'kernel_base', 'install_cat_element_root', 'RoleCandidate', 'role_of', 'category_of']

class Role(Enum):
    OBJECT = 'ObjectType'
    ELEMENT = 'ElementType'
    MORPHISM = 'MorphismType'

@contextmanager
def building_role_classes() -> Iterator[None]:
    ...

class CategoryPoint:

    def __init__(self) -> None:
        ...

    def defining_morphism(self) -> MorphismOfCategory:
        ...

    def parent(self) -> ObjectOfCategory:
        ...

    def category(self) -> Category:
        ...

    def __eq__(self, candidate: CategoryPoint | int) -> AppliedPredicate:
        ...

    def __ne__(self, candidate: CategoryPoint | int) -> Proposition:
        ...

    def __hash__(self) -> int:
        ...

class ObjectOfCategory(CategoryPoint):

    def __init_subclass__(cls) -> None:
        ...

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        ...

    def role_class(self, role: Role) -> type[CategoryPoint]:
        ...

    def role_source(self, role: Role) -> tuple[Category, Role]:
        ...

    def __init__(self) -> None:
        ...

    def category(self) -> Category:
        ...

    def __eq__(self, candidate: CategoryPoint | int) -> AppliedPredicate:
        ...

    def __ne__(self, candidate: CategoryPoint | int) -> Proposition:
        ...

    def __hash__(self) -> int:
        ...

class ElementOfObject(CategoryPoint):
    ...

class MorphismOfCategory(ObjectOfCategory):

    def category(self) -> Category:
        ...

    def base_category(self) -> Category:
        ...

    def domain(self) -> ObjectOfCategory:
        ...

    def codomain(self) -> ObjectOfCategory:
        ...

    def __mul__(self, first: MorphismOfCategory) -> MorphismOfCategory:
        ...

    def __eq__(self, candidate: CategoryPoint | int) -> AppliedPredicate:
        ...

    def __ne__(self, candidate: CategoryPoint | int) -> Proposition:
        ...

    def __hash__(self) -> int:
        ...

def kernel_base(role: Role) -> type[CategoryPoint]:
    ...

def install_cat_element_root(root: type[CategoryPoint]) -> None:
    ...
type RoleCandidate = CategoryPoint | int

def role_of(candidate: RoleCandidate) -> Role | None:
    ...

def category_of(value: CategoryPoint, role: Role) -> Category:
    ...
