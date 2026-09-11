from collections.abc import Callable

from sage_categories.cat.category import Category as Category
from sage_categories.kernel.compiler import compiler as compiler
from sage_categories.kernel.roles import (
    CategoryPoint as CategoryPoint,
)
from sage_categories.kernel.roles import (
    MorphismOfCategory as MorphismOfCategory,
)
from sage_categories.kernel.roles import (
    ObjectOfCategory as ObjectOfCategory,
)
from sage_categories.kernel.roles import (
    Role as Role,
)
from sage_categories.kernel.roles import (
    RoleCandidate as RoleCandidate,
)
from sage_categories.kernel.roles import (
    category_of as category_of,
)
from sage_categories.kernel.roles import (
    is_category as is_category,
)
from sage_categories.kernel.roles import (
    role_of as role_of,
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

def install_functor_declaration_readers(placement: FunctorDeclarationReader, inheritance: FunctorDeclarationReader, point: FunctorDeclarationReader) -> None: ...
def traces_placement(functor: MorphismOfCategory) -> bool: ...
def traces_inheritance(functor: MorphismOfCategory) -> bool: ...
def declares_point(functor: MorphismOfCategory) -> bool: ...
def is_placed(candidate: RoleCandidate, category: Category) -> bool: ...
def is_subcategory(inner: Category, outer: Category) -> bool: ...
def common_ancestor(first: Category, second: Category) -> Category | None: ...
def place(value: ObjectOfCategory, category: Category) -> None: ...
def refine[Value: ObjectOfCategory](value: Value, target: Category) -> Value: ...
