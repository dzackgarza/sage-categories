"""Local declarations for the poset-product design specimen, a universal-construction realization.

``U: Posets() -> Sets()`` is the retained composite of the inclusion into ``Relations()``
with the first projection, ``(X, R) |-> X``. The poset leaf states once that ``U`` creates
the limits of every discrete shape, by placing ``U`` in
``Fun(Posets(), Sets()).CreatesLimits(Discrete)``: a functor's theorem is the property
subcategory it is constructed into. The generic creates-limits construction then supplies
the lifted cone, its monotone projections, and the universal morphism, and
``Posets().Products()(P, Q)`` is inherited from ``Cat``. The leaf writes no product code.
"""

from __future__ import annotations

from sympy import assume


U = Relations().product_projection(0) * Fun(Posets(), Relations()).Monomorphisms().Isofibrations().Full()()

# The componentwise-order theorem: the apex of the lifted set-product cone carries the
# order ``x <= y`` iff ``x_i <= y_i`` for every ``i``, and applying ``U`` to the lifted
# cone returns the selected set-product cone. ``U`` is already constructed, so the
# statement refines it into ``Fun(Posets(), Sets()).CreatesLimits(Discrete)``.
assume(U.is_limit_creating(Discrete))
