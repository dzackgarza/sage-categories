"""Local declarations for the ``PointedSets()`` design specimen, a chosen-datum fibration.

``PointedSets()`` is ``Sets().CosliceUnder(Sets().Terminal())``, the coslice under the
one-point set; the generic coslice construction owns its objects ``(X, x: 1 -> X)``, its
basepoint-preserving maps, its constructor, and its retained projection to
``Fun([1], Sets())``. This class declares itself the implementation of that coslice by
selecting its identity functor, selects the retained projection composed with evaluation
at the codomain as its structure functor to ``Sets()``, adds no operation, and
wires no constructor.
"""

from __future__ import annotations


class PointedSetsCategory(Category):
    """Implement ``Sets().CosliceUnder(Sets().Terminal())``; a pointed set is the arrow ``x: 1 -> X`` the coslice retains."""

    class ObjectType:
        """The coslice object ``x: 1 -> X``; the coslice supplies the basepoint and the underlying set."""

    class ElementType:
        """Inherit the points of ``X`` through the structure functor to ``Sets()``."""

    class MorphismType:
        """Inherit the basepoint-preserving maps of the coslice."""

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Declare the implementation of the coslice and select its projection to ``Sets()``.

        The identity functor of the coslice is the whole implementation declaration. The
        functor ``(X, x) |-> X`` is the retained coslice projection composed with
        ``Fun([1], Sets()).ev(1)``; the leaf writes no action for it.
        """
        x = Sets().CosliceUnder(Sets().Terminal())
        underlying_set = Fun([1], Sets()).ev(1) * x.projection()
        return (End_Cat(x).one(), underlying_set)
