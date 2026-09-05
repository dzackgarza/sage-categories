from dataclasses import dataclass
from sage_categories.cat.canonical import FinitePresentedCategory as FinitePresentedCategory
from sage_categories.cat.cat_constructions import LimitCategory as LimitCategory
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.functors import Fun as Fun, FunctorCategory as FunctorCategory
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import OppositeCategory as OppositeCategory, opposite_morphism as opposite_morphism
from sage_categories.cat.predicates import Unknown as Unknown, UnknownClass as UnknownClass, ask as ask
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict

@dataclass(frozen=True)
class FiniteCategoryData:
    objects: tuple[CategoryOfCategories.ElementType, ...]
    morphisms: tuple[MorphismCategory.ObjectType, ...]

def position[Value: CategoryOfCategories.ElementType](values: tuple[Value, ...], value: Value) -> int:
    ...

def equal(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> bool:
    ...

def finite_category(category: CategoryOfCategories.ElementType) -> FiniteCategoryData | UnknownClass:
    ...
