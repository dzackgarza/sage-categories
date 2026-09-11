from collections.abc import Callable

from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory as LimitConesCategory
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = [
    "binary_product_data",
    "curry",
    "currying",
    "evaluation",
    "natural_isomorphism",
    "pair_maps",
    "power_data",
    "power_functor",
    "precompose",
    "product_functor",
    "terminal_map",
    "transpose",
    "uncurry",
]

def pair_maps(base: Category, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType: ...
def binary_product_data(base: Category, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> LimitConesCategory.ObjectType: ...
def power_data(base: Category, value: CategoryOfCategories.ElementType, degree: int) -> LimitConesCategory.ObjectType: ...
def terminal_map(base: Category, value: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...
@cached_function
def power_functor(base: Category, degree: int) -> Functor: ...
def product_functor(base: Category) -> Functor: ...
def precompose(along: Functor, target: Category) -> Functor: ...
def curry(functor: Functor) -> Functor: ...
def uncurry(functor: Functor) -> Functor: ...
def transpose(functor: Functor) -> Functor: ...
def evaluation(first: Category, target: Category) -> Functor: ...
def currying(first: Category, second: Category, target: Category) -> CategoryOfCategories.ElementType: ...
def natural_isomorphism(
    first: Functor,
    second: Functor,
    components: Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType],
    inverses: Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType],
) -> NaturalTransformation: ...
