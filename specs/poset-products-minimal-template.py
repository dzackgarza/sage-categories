"""Design specimen for componentwise order on a lifted set limit.

The leaf supplies its order predicate and the existing monotone-map constructor.
``with_limit_lifting`` builds the cone, projections, and universal morphism.
The finite executable consumer is in ``tests/kernel/test_lifted_limits.sage``.
"""

from __future__ import annotations

from sage_categories.cat.cones import LimitConesCategory


class ComponentwiseOrder(Predicate):
    """For every vertex i, compare c.leg(i)(x) <= c.leg(i)(y) in K(i).

    This is a poset-owned predicate. Its exact handlers evaluate the quantified
    order proposition for the supplied diagram and set-limit presentation.
    """

    name = "componentwise_order"


componentwise_order = ComponentwiseOrder()


class PosetsCategory(Category):
    """Extend the poset declaration in poset-minimal-template.py."""

    def lift_order(self, K: Cat().MorphismType, c: LimitConesCategory.ObjectType) -> Posets().ObjectType:
        """Put the componentwise partial order on the selected set-limit apex."""
        return self.from_predicate(c.apex(), lambda x, y: componentwise_order(K, c, x, y))

    def to_sets(self) -> Cat().MorphismType:
        """Define the faithful, limit-preserving isofibration to Sets()."""
        D = Sets()

        def on_object(P: self.ObjectType) -> D.ObjectType:
            return P._relation.ambient_object().product_projection(0).codomain()

        def on_morphism(f: self.MorphismType) -> D.MorphismType:
            source = on_object(f.domain())
            target = on_object(f.codomain())
            return Mor(D)(source, target)(f)

        U = Fun(self, D).Faithful().Isofibrations().PreservesLimits(Discrete)(on_object, on_morphism)
        return U.with_limit_lifting(Discrete, self.lift_order, self.construct_morphism)

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the identity of ``Relations().PartialOrder()`` and ``U``."""
        x = Relations().PartialOrder()
        return (End_Cat(x).one(), self.to_sets())
