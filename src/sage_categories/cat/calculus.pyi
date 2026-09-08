from collections.abc import Callable
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.sage_runtime import cached_function
__all__ = ['pair_maps', 'binary_product_data', 'power_data', 'terminal_map', 'power_functor', 'product_functor', 'precompose', 'curry', 'uncurry', 'transpose', 'evaluation', 'currying', 'natural_isomorphism']

def pair_maps(base: Category, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...

def binary_product_data(base: Category, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> LimitConesCategory.ObjectType:
    ...

def power_data(base: Category, value: CategoryOfCategories.ElementType, degree: int) -> LimitConesCategory.ObjectType:
    ...

def terminal_map(base: Category, value: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
    ...

@cached_function
def power_functor(base: Category, degree: int) -> Functor:
    ...

def product_functor(base: Category) -> Functor:
    ...

def precompose(along: Functor, target: Category) -> Functor:
    ...

def curry(functor: Functor) -> Functor:
    ...

def uncurry(functor: Functor) -> Functor:
    ...

def transpose(functor: Functor) -> Functor:
    ...

def evaluation(first: Category, target: Category) -> Functor:
    ...

def currying(first: Category, second: Category, target: Category) -> CategoryOfCategories.ElementType:
    ...

def natural_isomorphism(first: Functor, second: Functor, components: Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType], inverses: Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType]) -> NaturalTransformation:
    ...
