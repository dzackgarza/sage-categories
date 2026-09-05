from collections.abc import Iterator
from contextlib import contextmanager
from enum import Enum
from sage_categories.cat.category import Category
__all__ = ['Role', 'building_role_classes', 'CategoryPoint', 'prepare_category_subclass', 'ObjectOfCategory', 'ElementOfObject', 'MorphismOfCategory', 'install_category_object_class', 'is_category', 'category_universal_class', 'kernel_base', 'install_cat_element_root', 'RoleCandidate', 'role_of', 'category_of']

class Role(Enum):
    OBJECT = 'ObjectType'
    ELEMENT = 'ElementType'
    MORPHISM = 'MorphismType'

@contextmanager
def building_role_classes() -> Iterator[None]:
    ...

class CategoryPoint:

    def __setattr__[State](self, name: str, value: State) -> None:
        ...

    def __hash__(self) -> int:
        ...

def prepare_category_subclass(cls) -> None:
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

class ElementOfObject(CategoryPoint):
    ...

class MorphismOfCategory(ObjectOfCategory):
    ...

def install_category_object_class(compiled: type[CategoryPoint]) -> None:
    ...

def is_category(value: CategoryPoint) -> bool:
    ...

def category_universal_class() -> type[CategoryPoint]:
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
