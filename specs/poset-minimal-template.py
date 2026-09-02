"""Local declarations for the ``Relations()`` and ``Posets()`` design specimen.

``Relations()`` constructs a relation from its subobject ``R -> X * X`` and selects the
retained first projection ``(X, R) |-> X`` to ``Sets()``. It declares the ``PartialOrder``
axiom together with the proposition deciding it, applying a new SymPy predicate with its
exact handlers. ``Posets()`` is ``Relations().PartialOrder()``; it binds to that implicit
subcategory to add order comparison and monotone maps, and wires no constructor.
"""

from __future__ import annotations

from collections.abc import Callable

from sympy import ask
from sympy.assumptions import Predicate
from sympy.logic.boolalg import Boolean

from ._relations_sage import sage_is_partial_order


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
        """Inherit the points of ``X`` through the first projection."""

    class MorphismType:
        """Implement relation-preserving set maps."""

    def partial_order(self, R: Relations().ObjectType) -> Boolean:
        """State the proposition deciding membership in ``Relations().PartialOrder()``."""
        return partial_order_laws(owned_value_atom(R))

    PartialOrder = Axiom(partial_order)

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
        """Select the first projection ``(X, R) |-> X`` for inherited set operations.

        A relation inherits the structure of its set ``X``, so only the first projection
        is selected. The projection to ``R`` stays an ordinary retained functor.
        """
        return (self.product_projection(0),)


class PosetsCategory(Category):
    """Bind to ``Relations().PartialOrder()`` to add order comparison and monotone maps."""

    _base_category_class_and_axiom = (RelationsCategory, "PartialOrder")

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


@partial_order_laws.register(OwnedValueAtom)
def decide_partial_order(
    R: OwnedValueAtom,
    assumptions: Boolean,
) -> bool | None:
    """Decide the partial-order laws for exact supported relations.

    The guard asks an exact subquestion; the finite case runs an exhaustive check in the
    private engine module ``_relations_sage.py``.
    """
    match R.owned_value():
        case relation if ask(relation.ambient_object().is_finite()):
            return sage_is_partial_order(relation)
        case _:
            return None
