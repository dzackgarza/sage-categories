from collections.abc import Callable

from sage_categories.cat.category import Category
from sage_categories.kernel.roles import (
    CategoryPoint,
    MorphismOfCategory,
    RoleCandidate,
)

__all__ = [
    "FunctorDeclarationReader",
    "common_ancestor",
    "declares_point",
    "install_functor_declaration_readers",
    "is_placed",
    "is_subcategory",
    "place",
    "refine",
    "traces_inheritance",
    "traces_placement",
]
type FunctorDeclarationReader = Callable[[MorphismOfCategory], bool]

def install_functor_declaration_readers(placement: FunctorDeclarationReader, inheritance: FunctorDeclarationReader, point: FunctorDeclarationReader) -> None:
    ...

def traces_placement(functor: MorphismOfCategory) -> bool:
    ...

def traces_inheritance(functor: MorphismOfCategory) -> bool:
    ...

def declares_point(functor: MorphismOfCategory) -> bool:
    ...

def is_placed(candidate: RoleCandidate, category: Category) -> bool:
    ...

def is_subcategory(inner: Category, outer: Category) -> bool:
    ...

def common_ancestor(first: Category, second: Category) -> Category | None:
    ...

def place(value: CategoryPoint, category: Category) -> None:
    ...

def refine[Value: CategoryPoint](value: Value, target: Category) -> Value: ...
