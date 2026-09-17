from collections.abc import Callable
from sage_categories.cat.category import Category as Category
from sage_categories.kernel import compiler as compiler
from sage_categories.kernel.roles import CategoryPoint as CategoryPoint, MorphismOfCategory as MorphismOfCategory, ObjectOfCategory as ObjectOfCategory, Role as Role, RoleCandidate as RoleCandidate, category_of as category_of, is_category as is_category, role_of as role_of
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

def place(value: ObjectOfCategory, category: Category) -> None:
    ...

def refine[Value: ObjectOfCategory](value: Value, target: Category) -> Value:
    ...
