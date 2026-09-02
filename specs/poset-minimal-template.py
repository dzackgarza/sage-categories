"""Local declarations for the ``Relations()`` and ``Posets()`` design specimen.

``Relations()`` is sets with additional structure, a structure category: its datum is
``(X, R <= X * X)``, and it declares its structure functor to ``Sets()``,
``(X, R) |-> X``, as ``Fun(Relations(), Sets()).Fibrations()()``. It declares the
``PartialOrder`` axiom together with the private proposition deciding it, applying a new
SymPy predicate; the kernel generates the public ``R.is_partial_order()``. ``Posets()`` is
``Relations().PartialOrder()``, its axiom subcategory, and inherits that functor; the poset
class declares itself the implementation of that implicit subcategory by selecting its
identity functor as a structure functor, declares its own forgetful structure functor to
``Sets()`` with its theorem, adds order comparison and monotone maps, and wires no
constructor.
"""

from __future__ import annotations

from collections.abc import Callable

from sympy.assumptions import Predicate
from sympy.logic.boolalg import Boolean


class PartialOrderPredicate(Predicate):
    """State the partial-order laws for an owned relation."""

    name = "partial_order"


partial_order_laws = PartialOrderPredicate()


class RelationsCategory(Category):
    """Implement relations ``R -> X * X`` over varying ``X``."""

    class ObjectType:
        """Retain the relation subobject."""

        def __init__(
            self,
            relation: Sets().Subobjects(Sets().Products()(X, X)).ObjectType,
        ) -> None:
            """Retain the relation subobject; its codomain ``X * X`` determines ``X``."""
            self._relation = relation

    class ElementType:
        """Inherit the points of ``X`` through the structure functor to ``Sets()``."""

    class MorphismType:
        """Implement relation-preserving set maps."""

    def _partial_order(self, R: Relations().ObjectType) -> Boolean:
        """State the proposition deciding membership in ``Relations().PartialOrder()``."""
        return partial_order_laws(R)

    PartialOrder = Axiom(_partial_order)

    def __call__(
        self,
        relation: Sets().Subobjects(Sets().Products()(X, X)).ObjectType,
    ) -> Relations().ObjectType:
        """Construct the relation with subobject ``relation``."""
        return self.ObjectType(relation)

    def from_predicate(
        self,
        X: Sets().ObjectType,
        predicate: Callable[[Sets().ElementType, Sets().ElementType], Boolean],
    ) -> Relations().ObjectType:
        """Construct the relation whose subobject ``predicate`` selects in ``X * X``."""
        return self(Sets().Subobjects(Sets().Products()(X, X)).from_predicate(predicate))

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Declare the forgetful fibration ``(X, R) |-> X`` to ``Sets()``.

        A relation inherits the structure of its set ``X`` through this functor; it
        computes nothing, so the leaf writes no action for it.
        """
        return (Fun(Relations(), Sets()).Fibrations()(),)


class PosetsCategory(Category):
    """Implement ``Relations().PartialOrder()``: add order comparison and monotone maps."""

    class ObjectType:
        """Add the operations the partial order supplies."""

    class ElementType:
        """Add order comparison to points of a poset."""

        def __le__(self, other: Posets().ElementType) -> Boolean:
            """Return the proposition ``self <= other``."""
            relation = self.parent()._relation
            return relation.membership_proposition(relation.ambient_object()(self, other))

    class MorphismType:
        """Implement monotone maps."""

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the identity of ``Relations().PartialOrder()`` and declare ``U``.

        The identity functor of that category is the whole implementation declaration; the
        kernel constructs its inclusion into ``Relations()``. The forgetful structure
        functor ``U: Posets() -> Sets()`` is declared with its theorem, creation of the
        limits of every discrete shape (poset-products template).
        """
        x = Relations().PartialOrder()
        return (
            End_Cat(x).one(),
            Fun(Posets(), Sets()).Fibrations().CreatesLimits(Discrete)(),
        )
