from sage_categories.algebra.algebras import AlgebraCategory
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory

__all__ = ["restrict_algebra_scalars"]

def restrict_algebra_scalars(
    source: AlgebraCategory,
    target: AlgebraCategory,
    scalar_morphism: MorphismCategory.ObjectType,
) -> Functor: ...
