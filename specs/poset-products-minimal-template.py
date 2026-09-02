"""Local declarations for the poset-product design specimen, a universal-construction realization.

``Posets()`` is sets with additional structure, a structure category, so the poset leaf
defines its own functors to the categories it inherits methods from. Its forgetful
structure functor ``U: Posets() -> Sets()``, ``(X, R) |-> X``, computes nothing. The leaf
declares it as the zero-argument call on the property subcategory of
``Fun(Posets(), Sets())`` that states everything known about it: a fibration that creates
the limits of every discrete shape. A functor's theorem is the property subcategory it is
constructed into. The generic creates-limits construction then supplies the lifted cone,
its monotone projections, and the universal morphism, and ``Posets().Products()(P, Q)`` is
inherited from ``Cat``. The leaf writes no product code.
"""

from __future__ import annotations


class PosetsCategory(Category):
    """Implement ``Relations().PartialOrder()``: declare the forgetful functor with its theorem."""

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the identity of ``Relations().PartialOrder()`` and declare ``U``.

        The componentwise-order theorem: the apex of the lifted set-product cone carries the
        order ``x <= y`` iff ``x_i <= y_i`` for every ``i``, and applying ``U`` to the lifted
        cone returns the selected set-product cone. ``CreatesLimits(Discrete)`` states it.
        """
        x = Relations().PartialOrder()
        return (
            End_Cat(x).one(),
            Fun(Posets(), Sets()).Fibrations().CreatesLimits(Discrete)(),
        )
