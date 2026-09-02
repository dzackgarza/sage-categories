"""Local declarations for the poset-product design specimen, a universal-construction realization.

``Posets()`` is sets with additional structure, a structure category, so the poset leaf
defines its own functors to the categories it inherits methods from. Its structure
functor ``U: Posets() -> Sets()`` sends a poset to its underlying set, ``(X, R) |-> X``,
never to its relation. The leaf defines ``U`` by its two actions and constructs it into
the strongest property subcategory of ``Fun(Posets(), Sets())`` that states what is known
about it: a fibration that creates the limits of every discrete shape. A functor's theorem
is the property subcategory it is constructed into. The generic creates-limits
construction then supplies the lifted cone, its monotone projections, and the universal
morphism, and ``Posets().Products()(P, Q)`` is inherited from ``Cat``. The leaf writes no
product code.
"""

from __future__ import annotations


class PosetsCategory(Category):
    """Implement ``Relations().PartialOrder()``: define the functor to ``Sets()`` with its theorem."""

    def to_sets(self) -> Cat().MorphismType:
        """Define ``U: Posets() -> Sets()``, ``(X, R) |-> X`` and ``f |-> f``, creating discrete limits.

        The componentwise-order theorem: the apex of the lifted set-product cone carries the
        order ``x <= y`` iff ``x_i <= y_i`` for every ``i``, and applying ``U`` to the lifted
        cone returns the selected set-product cone. ``CreatesLimits(Discrete)`` states it.
        """
        D = Sets()

        def on_object(P: self.ObjectType) -> D.ObjectType:
            return P._relation.ambient_object().product_projection(0).codomain()

        def on_morphism(f: self.MorphismType) -> D.MorphismType:
            source = on_object(f.domain())
            target = on_object(f.codomain())
            return Mor(D)(source, target)(f)

        return Fun(self, D).Fibrations().CreatesLimits(Discrete)(on_object, on_morphism)

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the identity of ``Relations().PartialOrder()`` and ``U``."""
        x = Relations().PartialOrder()
        return (End_Cat(x).one(), self.to_sets())
