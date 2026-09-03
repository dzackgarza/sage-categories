"""Finite-set design specimen for the axiom declaration contract.

This pseudocode shows only the declarations owned by ``Sets()`` for its ``Finite`` axiom.
The private proposition deciding membership in ``Sets().Finite()`` uses methods that
already exist on ``Sets()``; ``Sets().Finite()`` exists implicitly, the kernel
constructs its structure functor to ``Sets()``, and ``cat_kernel`` generates ``X.is_finite()``.
A class implementing an axiom subcategory appears in the poset and finite-poset templates.
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

    def _finite(self, X: Sets().ObjectType) -> Boolean:
        """State the proposition deciding membership in ``Sets().Finite()``."""
        return X.cardinality() < aleph0

    Finite = Axiom(_finite)
