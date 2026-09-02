"""Finite-set design specimen for the axiom declaration contract.

This pseudocode shows only the declarations owned by ``Sets()`` for its ``Finite`` axiom.
The proposition deciding membership in ``Sets().Finite()`` uses methods that already exist
on ``Sets()``; ``Sets().Finite()`` exists implicitly, and the kernel constructs its
structure functor to ``Sets()`` and generates ``X.is_finite()``.
"""

from __future__ import annotations

from sympy.logic.boolalg import Boolean


class SetsCategory(Category):
    """Implement sets, elements, and total set maps."""

    class ObjectType:
        """Implement sets."""

    class ElementType:
        """Implement elements of represented sets."""

    class MorphismType:
        """Implement total set maps."""

    def finite(self, X: Sets().ObjectType) -> Boolean:
        """State the proposition deciding membership in ``Sets().Finite()``."""
        return X.cardinality() < aleph0

    Finite = Axiom(finite)


class FiniteSetsCategory(Category):
    """Bind to ``Sets().Finite()`` to add finite-only operations.

    The subcategory has exactly the constructors of ``Sets()``.
    """

    _base_category_class_and_axiom = (SetsCategory, "Finite")

    class ObjectType:
        """Inherit the set surface under established finiteness."""

    class ElementType:
        """Add no finite-set element operation."""

    class MorphismType:
        """Add no finite-set morphism operation."""
