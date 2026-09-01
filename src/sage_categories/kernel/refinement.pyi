from sage_categories.cat.category import Category
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, RoleCandidate
__all__ = ['traces_placement', 'is_placed', 'is_subcategory', 'common_ancestor', 'place', 'refine']

def traces_placement(functor: MorphismOfCategory) -> bool:
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
