from collections.abc import Callable
from sage_categories.cat.category import Category
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, RoleCandidate
__all__ = ['FunctorDeclarationReader', 'install_functor_declaration_readers', 'traces_placement', 'traces_inheritance', 'is_placed', 'is_subcategory', 'common_ancestor', 'place', 'refine']
type FunctorDeclarationReader = Callable[[MorphismOfCategory], bool]

def install_functor_declaration_readers(placement: FunctorDeclarationReader, inheritance: FunctorDeclarationReader) -> None:
    ...

def traces_placement(functor: MorphismOfCategory) -> bool:
    ...

def traces_inheritance(functor: MorphismOfCategory) -> bool:
    ...

def is_placed(candidate: RoleCandidate, category: Category) -> bool:
    ...

def is_subcategory(inner: Category, outer: Category) -> bool:
    ...

def common_ancestor(first: Category, second: Category) -> Category | None:
    ...

def place(value: CategoryPoint, category: Category) -> None:
    ...

def refine(value: CategoryPoint, target: Category) -> None:
    ...
