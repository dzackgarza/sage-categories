from collections.abc import Sequence

from sage_categories.algebra.algebras import AlgebraCategory
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Functor

__all__ = [
    "integer_free_algebra",
    "integer_free_algebra_generator",
    "integer_free_algebra_homomorphism",
    "presented_algebra_diagram",
    "presented_algebra_factor",
    "presented_algebra_presentation",
    "presented_algebra_projection",
    "retain_split_algebra_presentation",
]

type AlgebraMap = AlgebraCategory.MorphismType

def integer_free_algebra(
    algebras: AlgebraCategory, names: Sequence[str]
) -> AlgebraCategory.ObjectType: ...
def integer_free_algebra_generator(
    algebras: AlgebraCategory, algebra: AlgebraCategory.ObjectType, position: int
) -> CategoryOfCategories.ElementType: ...
def integer_free_algebra_homomorphism(
    algebras: AlgebraCategory,
    source: AlgebraCategory.ObjectType,
    target: AlgebraCategory.ObjectType,
    generator_images: Sequence[CategoryOfCategories.ElementType],
) -> AlgebraCategory.MorphismType: ...
def retain_split_algebra_presentation(
    algebras: AlgebraCategory,
    first: AlgebraMap,
    second: AlgebraMap,
    projection: AlgebraMap,
    section: AlgebraMap,
) -> AlgebraCategory.ObjectType: ...
def presented_algebra_diagram(
    algebras: AlgebraCategory, algebra: AlgebraCategory.ObjectType
) -> Functor: ...
def presented_algebra_presentation(
    algebras: AlgebraCategory, algebra: AlgebraCategory.ObjectType
) -> LimitConesCategory.ObjectType: ...
def presented_algebra_projection(
    algebras: AlgebraCategory, algebra: AlgebraCategory.ObjectType
) -> AlgebraMap: ...
def presented_algebra_factor(
    algebras: AlgebraCategory,
    algebra: AlgebraCategory.ObjectType,
    target: AlgebraCategory.ObjectType,
    coequalizing: AlgebraMap,
) -> AlgebraMap: ...
