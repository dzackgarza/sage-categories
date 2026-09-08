import sage_categories
from collections.abc import Callable, Hashable, Iterable, Iterator
from functools import cache
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from typing import Literal
__all__ = ['FiniteSetsCategory', 'FiniteSets']
type Map = Callable[[Hashable], Hashable]

class FiniteSetsCategory(Category[[Map], []]):

    class ObjectType(sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, values: tuple[Hashable, ...]) -> None:
            ...

        def representative(self, datum: Hashable) -> Hashable:
            ...

        @cache
        def point(self, datum: Hashable) -> FiniteSetsCategory.ElementType:
            ...

        def __iter__(self) -> Iterator[FiniteSetsCategory.ElementType]:
            ...

        def __len__(self) -> int:
            ...

        def __contains__(self, point: CategoryOfCategories.ElementType) -> bool:
            ...

    class ElementType(sage_categories.kernel.roles.ElementOfObject):

        def __init__(self, datum: Hashable) -> None:
            ...

        def datum(self) -> Hashable:
            ...

    class MorphismType(sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, pairs: tuple[tuple[Hashable, Hashable], ...]) -> None:
            ...

        def __call__(self, point: CategoryOfCategories.ElementType) -> FiniteSetsCategory.ElementType:
            ...

    def __call__(self, values: Iterable[Hashable]) -> FiniteSetsCategory.ObjectType:
        ...

    def Terminal(self) -> FiniteSetsCategory.ObjectType:
        ...

    def element_from_defining_morphism(self, arrow: MorphismCategory.ObjectType) -> FiniteSetsCategory.ElementType:
        ...

    def construct_morphism(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, action: Map) -> MorphismCategory.ObjectType:
        ...

    def construct_identity(self, value: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

    def colimit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

    def image_factorization(self, arrow: MorphismCategory.ObjectType) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
        ...

    def factor_through_monomorphism(self, mono: MorphismCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType | Literal[False]:
        ...

    @cache
    def hom_morphisms(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType) -> tuple[MorphismCategory.ObjectType, ...]:
        ...
FiniteSets: FiniteSetsCategory
