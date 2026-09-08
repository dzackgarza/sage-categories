"""Bimodule objects: one carrier with a left and a right action that commute.

``Bimodules(R, S, V)`` for monoid objects ``R`` and ``S`` of a monoidal category ``V``
(``specs/bimodules.md``).  An object is ``X`` in ``V`` with ``lambda: R (x) X -> X`` and
``rho: X (x) S -> X``, each satisfying its own module laws, such that the two ways of
acting on ``R (x) (X (x) S)`` agree.

A right ``S``-action is a left action of ``S`` in the reverse monoidal category, where
``x (x)^rev y = y (x) x`` (``cat/monoidal.py``, ``Reversed``), so both halves are
``Modules`` and neither needs a braiding.  The two halves are combined by the pullback of
their forgetful functors over ``V``, which is the one carrier, and the commuting law is
the equifier of the two composites on it; this is how ``Semirings`` combines its two
monoid structures (``cat/structured_objects.py``).
"""

from __future__ import annotations

__all__ = ["ActionPairsCategory", "BimoduleCategory", "Bimodules"]

from sage_categories.cat.cat_constructions import LimitSubcategory, limit_of_categories
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.modules import ModuleCategory, Modules
from sage_categories.cat.monoidal import MonoidalStructuresCategory, Reversed, SelfAction, tensor_morphism
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.structured_objects import EquifierCategory, MonoidCategory, Monoids
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method


class ActionPairsCategory(LimitSubcategory):
    """The pullback of the left and right module categories over their common carrier in ``V``.

    An object is ``(X_l, X_r, X)`` with ``X_l`` a left ``R``-module structure on ``X`` and
    ``X_r`` a right ``S``-module structure on the same ``X``.  Both legs are declared
    faithful isofibrations, so the pair inherits each action from its own side and the
    carrier once.
    """

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    @cached_method
    def to_left(self) -> Functor:
        return Fun(self, self.factor(0)).Faithful().Isofibrations()(
            lambda value: value.family_component(0), lambda arrow: arrow.family_component(0)
        )

    @cached_method
    def to_right(self) -> Functor:
        return Fun(self, self.factor(1)).Faithful().Isofibrations()(
            lambda value: value.family_component(1), lambda arrow: arrow.family_component(1)
        )

    def homomorphism(
        self,
        source: ActionPairsCategory.ObjectType,
        target: ActionPairsCategory.ObjectType,
        arrow: MorphismCategory.ObjectType,
    ) -> ActionPairsCategory.MorphismType:
        """The pair morphism over a carrier map ``f: X -> Y`` that preserves both actions."""
        left, right = self.factor(0), self.factor(1)
        return self.construct_morphism(
            source,
            target,
            (
                left.homomorphism(source.family_component(0), target.family_component(0), arrow),
                right.homomorphism(source.family_component(1), target.family_component(1), arrow),
                arrow,
            ),
        )

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.to_left(), self.to_right())


class BimoduleCategory(EquifierCategory):
    """``Bimodules(R, S, V)``: action pairs whose left and right actions commute."""

    class ObjectType:
        def left_action(self) -> MorphismCategory.ObjectType:
            """``lambda: R (x) X -> X``."""
            return self.family_component(0).action()

        def right_action(self) -> MorphismCategory.ObjectType:
            """``rho: X (x) S -> X``."""
            return self.family_component(1).action()

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(
        self,
        first: NaturalTransformation,
        second: NaturalTransformation,
        left: ModuleCategory,
        right: ModuleCategory,
        pairs: ActionPairsCategory,
    ) -> None:
        self._left, self._right, self._pairs = left, right, pairs
        super().__init__(first, second)

    def left_modules(self) -> ModuleCategory:
        """``Modules(R, V)``, the left half."""
        return self._left

    def right_modules(self) -> ModuleCategory:
        """``Modules(S, V^rev)``, the right half; its objects are the right ``S``-modules."""
        return self._right

    def monoidal_structure(self) -> MonoidalStructuresCategory.ObjectType:
        return self._left.actegory().monoidal_structure()

    def underlying_category(self) -> Category:
        return self._left.underlying_category()

    @cached_method
    def to_left(self) -> Functor:
        """The retained leg to the left module category."""
        return self._pairs.to_left() * Fun.full_subcategory_monomorphism(self, self._pairs)

    @cached_method
    def to_right(self) -> Functor:
        """The retained leg to the right module category."""
        return self._pairs.to_right() * Fun.full_subcategory_monomorphism(self, self._pairs)

    @cached_method
    def forgetful(self) -> Functor:
        """``U: Bimodules(R, S, V) -> V``, the one carrier both actions live on."""
        return self._left.forgetful() * self.to_left()

    def __call__(
        self,
        left_action: MorphismCategory.ObjectType,
        right_action: MorphismCategory.ObjectType,
    ) -> BimoduleCategory.ObjectType:
        """The bimodule with these two actions; their common codomain is the carrier."""
        assert left_action.codomain() is right_action.codomain(), (
            f"{left_action!r} and {right_action!r} do not act on one carrier"
        )
        return super().__call__(
            self._pairs((self._left(left_action), self._right(right_action), left_action.codomain()))
        )

    def homomorphism(
        self,
        source: BimoduleCategory.ObjectType,
        target: BimoduleCategory.ObjectType,
        arrow: MorphismCategory.ObjectType,
    ) -> BimoduleCategory.MorphismType:
        """The bimodule morphism over a map of ``V`` preserving both actions; fullness makes it a morphism here."""
        return self._pairs.homomorphism(source, target, arrow)


@cached_function(key=identity_key)
def Bimodules(
    left_scalars: MonoidCategory.ObjectType,
    right_scalars: MonoidCategory.ObjectType,
    monoidal: MonoidalStructuresCategory.ObjectType,
) -> BimoduleCategory:
    """``Bimodules(R, S, V)``: objects of ``V`` carrying a left ``R``-action and a commuting right ``S``-action.

    Both scalars are monoid objects of ``V``.  The right half reads ``S`` in ``V^rev``,
    where its own multiplication and unit present the opposite monoid, so a caller writes
    no opposite by hand.
    """
    reverse = Reversed(monoidal)
    monoids = Monoids(monoidal)
    for scalars in (left_scalars, right_scalars):
        assert scalars in monoids, f"{scalars!r} is not a monoid object of {monoidal.underlying_category()!r}"
    opposite = Monoids(reverse)(right_scalars.operation(), right_scalars.unit_morphism())
    left, right = Modules(left_scalars, SelfAction(monoidal)), Modules(opposite, SelfAction(reverse))
    pairs = limit_of_categories(
        cospan_diagram(Cat(), left.forgetful(), right.forgetful()), Cat().Pullbacks(), ActionPairsCategory
    )
    base, tensor = monoidal.underlying_category(), monoidal.tensor()
    carrier = left.forgetful() * pairs.to_left()
    scalars, co_scalars = left.carrier(), right.carrier()
    associator = monoidal.associator().inverse()
    triples = monoidal.associator().domain().domain()

    def commuting(value: CategoryOfCategories.ElementType, through_the_left: bool) -> MorphismCategory.ObjectType:
        """``lambda (1 (x) rho)`` and ``rho (lambda (x) 1) a^-1`` on ``R (x) (X (x) S)``."""
        x = value.family_component(2)
        lam, rho = value.family_component(0).action(), value.family_component(1).action()
        if through_the_left:
            return lam * tensor_morphism(tensor, Mor(base)(scalars, scalars).one(), rho)
        rebracket = associator.component(triples((scalars, x, co_scalars)))
        return rho * tensor_morphism(tensor, lam, Mor(base)(co_scalars, co_scalars).one()) * rebracket

    source = left.scalar_endofunctor() * right.scalar_endofunctor() * carrier
    transformations = Mor(Fun(pairs, base))
    return BimoduleCategory(
        transformations(source, carrier)(lambda value: commuting(value, True)),
        transformations(source, carrier)(lambda value: commuting(value, False)),
        left,
        right,
        pairs,
    )
