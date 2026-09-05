"""Local declarations for the ``FinitePosets()`` design specimen, a pullback-defined category.

``Posets().Finite()`` is the pullback in ``Cat`` of ``Sets().Finite()`` along the structure
functor ``U: Posets() -> Sets()``; it exists implicitly, and the pullback retains both
projections as its structure functors. This class declares itself its implementation by
selecting its identity functor, adds the algorithms that require finiteness, and wires no
constructor: ``Posets().Finite()`` has exactly the constructors of ``Posets()``. Engine
lowering lives in the neighboring private module ``_finite_poset_sage.py``.
"""

from __future__ import annotations

from ._finite_poset_sage import SagePoset, sage_poset


class FinitePosetsCategory(Category):
    """Implement ``Posets().Finite()``: add finite-poset algorithms."""

    class ObjectType:
        """Add the finite-poset algorithms."""

        def height(self) -> Cardinal().ObjectType:
            """Return the cardinality of a largest chain."""
            return Cardinal()(self._sage_poset().height())

        def width(self) -> Cardinal().ObjectType:
            """Return the cardinality of a largest antichain."""
            return Cardinal()(self._sage_poset().width())

        def linear_extension(self) -> FiniteTotallyOrderedSets().ObjectType:
            """Return a finite total order on the same underlying set extending this order."""
            return FiniteTotallyOrderedSets().from_sage(self._sage_poset().linear_extension())

        def _sage_poset(self) -> SagePoset:
            """Lower the finite order to the private Sage engine module."""
            return sage_poset(self)

    class ElementType:
        """Add no finite-poset element operation."""

    class MorphismType:
        """Add no finite-poset morphism operation."""

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Declare this class the implementation of ``Posets().Finite()``."""
        x = Posets().Finite()
        return (End_Cat(x).one(),)
