"""The layer downstream of the kernel and ``Cat`` (``specs/resolution.md``, D175).

``Cat`` defines functors; the kernel interprets an axiom declaration as a specifically
structured isofibration.  The work that needs both lives here: reading a functor's
declared properties to decide placement and inheritance, and generating each axiom's
property subcategory with its inclusion ``C.P() -> C`` and its predicate ``is_p()``.

This layer imports from the kernel and from ``Cat``; neither imports it, and no leaf
imports it.  So it hands its work down to the two layers below, and ``sage_categories``
calls ``install`` once ``Cat`` is loaded and before any category is declared.
"""

from sage_categories.cat_kernel import axioms as _axioms
from sage_categories.cat_kernel import functor_declarations as _functor_declarations

__all__ = ["install"]


def install() -> None:
    """Install this layer into the two layers below."""
    _functor_declarations.install()
    _axioms.install()
