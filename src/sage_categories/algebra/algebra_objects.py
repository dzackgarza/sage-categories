"""Unified public surface for base-relative algebra objects.

The mathematical owner is always :func:`Algebras`.  Concrete free-algebra execution,
retained presentations, and scalar change are evaluators or functors on that same owner;
none introduces a parallel algebra class.
"""

from sage_categories.algebra.algebra_scalar_change import restrict_algebra_scalars
from sage_categories.algebra.algebras import (
    AlgebraCategory,
    Algebras,
    select_module_monoidal_structure,
)
from sage_categories.algebra.presented_algebras import (
    integer_free_algebra,
    integer_free_algebra_generator,
    integer_free_algebra_homomorphism,
    presented_algebra_diagram,
    presented_algebra_factor,
    presented_algebra_presentation,
    presented_algebra_projection,
    retain_split_algebra_presentation,
)

__all__ = [
    "AlgebraCategory",
    "Algebras",
    "integer_free_algebra",
    "integer_free_algebra_generator",
    "integer_free_algebra_homomorphism",
    "presented_algebra_diagram",
    "presented_algebra_factor",
    "presented_algebra_presentation",
    "presented_algebra_projection",
    "restrict_algebra_scalars",
    "retain_split_algebra_presentation",
    "select_module_monoidal_structure",
]
