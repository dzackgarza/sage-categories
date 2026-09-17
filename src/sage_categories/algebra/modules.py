"""Unified public API for ordinary scalar-general module constructions.

This module is a façade only.  The mathematical owner remains the generic
``ModuleCategory`` returned by ``Modules(A, C)``; free modules, presentations,
and native ingestion retain their existing owners and are re-exported here so a
consumer does not switch APIs when moving between those constructions.
"""

from sage_categories.algebra.free_modules import (
    finite_free_basis,
    finite_free_basis_family,
    finite_free_injection,
    finite_free_matrix_morphism,
    finite_free_module,
    finite_free_projection,
    free_module_homomorphism,
    ordinary_modules,
    regular_module,
)
from sage_categories.algebra.module_adapters import sage_module_from_engine
from sage_categories.algebra.presented_modules import (
    finitely_presented_module,
    presented_module_diagram,
    presented_module_factor,
    presented_module_presentation,
    presented_module_projection,
    presented_module_relation,
    presented_module_zero,
    relation_matrix_morphism,
)
from sage_categories.cat.modules import (
    ModuleCategory,
    Modules,
    internal_endomorphism_module,
)

__all__ = [
    "ModuleCategory",
    "Modules",
    "finite_free_basis",
    "finite_free_basis_family",
    "finite_free_injection",
    "finite_free_matrix_morphism",
    "finite_free_module",
    "finite_free_projection",
    "finitely_presented_module",
    "free_module_homomorphism",
    "internal_endomorphism_module",
    "ordinary_modules",
    "presented_module_diagram",
    "presented_module_factor",
    "presented_module_presentation",
    "presented_module_projection",
    "presented_module_relation",
    "presented_module_zero",
    "regular_module",
    "relation_matrix_morphism",
    "sage_module_from_engine",
]
