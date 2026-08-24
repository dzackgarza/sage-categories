"""Minimal structured leaf for ``PartiallyOrderedSets()``.

A poset object is a pair ``(X, R)``. Here ``X`` is an owned set and ``R`` is
an owned subobject of ``X × X``. Category placement asserts that ``R`` is
reflexive, antisymmetric, and transitive.

The carrier projection ``(X, R) -> X`` is the only selected structural
functor. It supplies the inherited set surface. The relation remains defining
poset data.

The kernel owns ``ProductProjectionFunctor`` and all its object, element, and
arrow maps. The leaf only selects that standard functor.
"""

from __future__ import annotations


class PartiallyOrderedSetsCategory(Category):
    """The category of partially ordered sets and monotone maps."""

    class ObjectType(Implementation):
        """Implement a set equipped with a partial-order relation."""

        def __init__(
            self,
            *,
            category: PartiallyOrderedSetsCategory,
            underlying_set: SetsCategory.ObjectType,
            order_relation: SetSubobject,
        ) -> None:
            product = underlying_set.cartesian_product(underlying_set)
            assert order_relation.inclusion().codomain() is product
            self._underlying_set = underlying_set
            self._order_relation = order_relation
            super().__init__(category=category)

        def order_relation(self) -> SetSubobject:
            """Return the defining subobject of ``X × X``."""
            return self._order_relation

    class ElementType(Implementation):
        """Implement elements with the operation introduced by order."""

        def __le__(
            self,
            other: PartiallyOrderedSetsCategory.ElementType,
        ) -> Proposition:
            """Return the proposition that ``self <= other``."""
            assert self.parent() is other.parent()
            return self.parent().order_relation().contains_pair(self, other)

    class ArrowType(Implementation):
        """Implement monotone maps with the inherited arrow surface."""

    def __call__(
        self,
        underlying_set: SetsCategory.ObjectType,
        order_relation: SetSubobject,
    ) -> PartiallyOrderedSetsCategory.ObjectType:
        """Construct the asserted partial order ``(X, R)``."""
        return self.ObjectType(
            category=self,
            underlying_set=underlying_set,
            order_relation=order_relation,
        )

    def structure_functors(self) -> tuple[Functor, ...]:
        """Select the carrier projection used for inheritance."""
        carrier = ProductProjectionFunctor(0, self, Sets())
        return (carrier,)
