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

from typing import Literal

__all__ = [
    "ActionPairsCategory",
    "BimoduleCategory",
    "Bimodules",
    "fixed_tensor_functor",
    "induced_left_action",
    "induced_right_action",
    "relative_left_unitor",
    "relative_right_unitor",
    "relative_tensor",
    "relative_tensor_factor",
    "relative_tensor_morphism",
    "relative_tensor_preserved_factor",
]

from sage_categories.cat.calculus import curry, transpose
from sage_categories.cat.cat_constructions import (
    LimitSubcategory,
    _faithful_isofibration_projection,
    _retained_object_component,
    limit_of_categories,
)
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import cocone
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.limit_basis import (
    coequalizer_factor,
    coequalizer_presentation,
    parallel_pair,
)
from sage_categories.cat.modules import ModuleCategory, Modules
from sage_categories.cat.monoidal import (
    MonoidalStructuresCategory,
    Reversed,
    SelfAction,
    tensor_morphism,
    tensor_object,
)
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.structured_objects import (
    EquifierCategory,
    MonoidCategory,
    Monoids,
)
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method


@cached_function(key=identity_key)
def fixed_tensor_functor(
    monoidal: MonoidalStructuresCategory.ObjectType,
    value: CategoryOfCategories.ElementType,
    side: Literal["left", "right"],
) -> Functor:
    """Tensor by one fixed object using the supplied monoidal tensor."""
    curried = curry(monoidal.tensor())
    match side:
        case "left":
            return curried.on_object(value)
        case "right":
            return transpose(curried).on_object(value)


def _relative_tensor_parallel_pair(
    monoidal: MonoidalStructuresCategory.ObjectType,
    middle: CategoryOfCategories.ElementType,
    right_action: MorphismCategory.ObjectType,
    left_action: MorphismCategory.ObjectType,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    """The two balancing maps defining a relative tensor product."""
    base, tensor = monoidal.underlying_category(), monoidal.tensor()
    first, second = right_action.codomain(), left_action.codomain()
    triples = monoidal.associator().domain().domain()
    rebracket = monoidal.associator().component(triples((first, middle, second)))
    through_the_right = tensor_morphism(tensor, right_action, Mor(base)(second, second).one())
    through_the_left = tensor_morphism(tensor, Mor(base)(first, first).one(), left_action)
    return through_the_right, through_the_left * rebracket


@cached_function(key=identity_key)
def relative_tensor(
    monoidal: MonoidalStructuresCategory.ObjectType,
    middle: CategoryOfCategories.ElementType,
    right_action: MorphismCategory.ObjectType,
    left_action: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """The retained coequalizer map from the ordinary tensor to the relative tensor."""
    base = monoidal.underlying_category()
    first, second = right_action.codomain(), left_action.codomain()
    through_the_right, through_the_left = _relative_tensor_parallel_pair(
        monoidal,
        middle,
        right_action,
        left_action,
    )
    diagram = parallel_pair(through_the_right, through_the_left)
    shape = diagram.domain()
    source_vertex, target_vertex = shape(0), shape(1)
    family = base.Colimits(shape)

    selected_right = monoidal.right_unitor().component(first)
    selected_left = monoidal.left_unitor().component(second)
    match right_action is selected_right and left_action is selected_left:
        case True:
            product = tensor_object(monoidal.tensor(), first, second)
            identity = Mor(base)(product, product).one()
            family.with_universal_data(
                diagram,
                product,
                cocone(
                    diagram,
                    product,
                    lambda vertex: through_the_right if vertex is source_vertex else identity,
                ),
                lambda candidate: candidate.component(target_vertex),
            )
            return identity
        case False:
            family(diagram)
            return family.universal_data(diagram).leg(target_vertex)


def relative_tensor_factor(
    monoidal: MonoidalStructuresCategory.ObjectType,
    projection: MorphismCategory.ObjectType,
    arrow: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """Factor a balanced map through the retained relative-tensor coequalizer."""
    presentation = coequalizer_presentation(monoidal.underlying_category(), projection)
    return coequalizer_factor(presentation, arrow)


def relative_tensor_preserved_factor(
    monoidal: MonoidalStructuresCategory.ObjectType,
    projection: MorphismCategory.ObjectType,
    functor: Functor,
    arrow: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """Factor through the image of a relative tensor under a preserving functor."""
    presentation = coequalizer_presentation(monoidal.underlying_category(), projection)
    preserved = functor.preserved_colimit(presentation)
    return coequalizer_factor(preserved, arrow)


def induced_left_action(
    monoidal: MonoidalStructuresCategory.ObjectType,
    projection: MorphismCategory.ObjectType,
    scalars: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    left_action: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """Descend an outer left action through a relative-tensor coequalizer."""
    base, tensor = monoidal.underlying_category(), monoidal.tensor()
    first = left_action.codomain()
    triples = monoidal.associator().domain().domain()
    rebracket = monoidal.associator().inverse().component(triples((scalars, first, second)))
    acting = projection * tensor_morphism(tensor, left_action, Mor(base)(second, second).one()) * rebracket
    return relative_tensor_preserved_factor(
        monoidal,
        projection,
        fixed_tensor_functor(monoidal, scalars, "left"),
        acting,
    )


def induced_right_action(
    monoidal: MonoidalStructuresCategory.ObjectType,
    projection: MorphismCategory.ObjectType,
    first: CategoryOfCategories.ElementType,
    scalars: CategoryOfCategories.ElementType,
    right_action: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """Descend an outer right action through a relative-tensor coequalizer."""
    base, tensor = monoidal.underlying_category(), monoidal.tensor()
    second = right_action.codomain()
    triples = monoidal.associator().domain().domain()
    rebracket = monoidal.associator().component(triples((first, second, scalars)))
    acting = projection * tensor_morphism(tensor, Mor(base)(first, first).one(), right_action) * rebracket
    return relative_tensor_preserved_factor(
        monoidal,
        projection,
        fixed_tensor_functor(monoidal, scalars, "right"),
        acting,
    )


def relative_tensor_morphism(
    monoidal: MonoidalStructuresCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """The map of relative tensors induced by compatible maps of both factors."""
    underlying = target * tensor_morphism(monoidal.tensor(), first, second)
    return relative_tensor_factor(monoidal, source, underlying)


def relative_left_unitor(
    monoidal: MonoidalStructuresCategory.ObjectType,
    projection: MorphismCategory.ObjectType,
    left_action: MorphismCategory.ObjectType,
    unit_morphism: MorphismCategory.ObjectType,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    """``S ⊗_S Y ≅ Y`` induced by the admitted left action and monoid unit."""
    base, tensor = monoidal.underlying_category(), monoidal.tensor()
    carrier = left_action.codomain()
    identity = Mor(base)(carrier, carrier).one()
    forward = relative_tensor_factor(monoidal, projection, left_action)
    backward = projection * tensor_morphism(tensor, unit_morphism, identity) * monoidal.left_unitor().inverse().component(carrier)
    base.retain_inverses(forward, backward)
    return forward, backward


def relative_right_unitor(
    monoidal: MonoidalStructuresCategory.ObjectType,
    projection: MorphismCategory.ObjectType,
    right_action: MorphismCategory.ObjectType,
    unit_morphism: MorphismCategory.ObjectType,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    """``X ⊗_S S ≅ X`` induced by the admitted right action and monoid unit."""
    base, tensor = monoidal.underlying_category(), monoidal.tensor()
    carrier = right_action.codomain()
    identity = Mor(base)(carrier, carrier).one()
    forward = relative_tensor_factor(monoidal, projection, right_action)
    backward = projection * tensor_morphism(tensor, identity, unit_morphism) * monoidal.right_unitor().inverse().component(carrier)
    base.retain_inverses(forward, backward)
    return forward, backward


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
        projection = _faithful_isofibration_projection(self, 0)
        projection.retain_cartesian_lifts(lambda morphism, target: self._cartesian_lift(0, morphism, target))
        return projection

    @cached_method
    def to_right(self) -> Functor:
        projection = _faithful_isofibration_projection(self, 1)
        projection.retain_cartesian_lifts(lambda morphism, target: self._cartesian_lift(1, morphism, target))
        return projection

    def _cartesian_lift(
        self,
        index: int,
        morphism: MorphismCategory.ObjectType,
        target: ActionPairsCategory.ObjectType,
    ) -> ActionPairsCategory.MorphismType:
        """Pull back the other module action along the shared carrier isomorphism."""
        selected, other = self.factor(index), self.factor(1 - index)
        carrier_map = selected.forgetful().on_morphism(morphism)
        other_target = _retained_object_component(target, 1 - index)
        other_lift = other.forgetful().cartesian_lift(carrier_map, other_target)
        match index:
            case 0:
                source = self((morphism.domain(), other_lift.domain(), carrier_map.domain()))
                arrows = (morphism, other_lift, carrier_map)
            case 1:
                source = self((other_lift.domain(), morphism.domain(), carrier_map.domain()))
                arrows = (other_lift, morphism, carrier_map)
            case _:
                raise AssertionError(f"{index} is not a bimodule-action projection index")
        return self.construct_morphism(source, target, arrows)

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
                left.homomorphism(_retained_object_component(source, 0), _retained_object_component(target, 0), arrow),
                right.homomorphism(_retained_object_component(source, 1), _retained_object_component(target, 1), arrow),
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
            return _retained_object_component(self, 0).action()

        def right_action(self) -> MorphismCategory.ObjectType:
            """``rho: X (x) S -> X``."""
            return _retained_object_component(self, 1).action()

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
        projection = self._pairs.to_left() * Fun.full_subcategory_monomorphism(self, self._pairs)
        projection.retain_cartesian_lifts(lambda morphism, target: self._cartesian_lift(0, morphism, target))
        return projection

    @cached_method
    def to_right(self) -> Functor:
        """The retained leg to the right module category."""
        projection = self._pairs.to_right() * Fun.full_subcategory_monomorphism(self, self._pairs)
        projection.retain_cartesian_lifts(lambda morphism, target: self._cartesian_lift(1, morphism, target))
        return projection

    def _cartesian_lift(
        self,
        index: int,
        morphism: MorphismCategory.ObjectType,
        target: BimoduleCategory.ObjectType,
    ) -> BimoduleCategory.MorphismType:
        """Restrict the action-pair lift; commuting is preserved by conjugation."""
        match index:
            case 0:
                projection = self._pairs.to_left()
            case 1:
                projection = self._pairs.to_right()
            case _:
                raise AssertionError(f"{index} is not a bimodule-action projection index")
        lift = projection.cartesian_lift(morphism, target)
        refine(lift.domain(), self)
        return self.restrict_morphism(lift)

    @cached_method
    def forgetful(self) -> Functor:
        """``U: Bimodules(R, S, V) -> V``, the one carrier both actions live on."""
        return self._left.forgetful() * self.to_left()

    def structure_functors(self) -> tuple[Functor, ...]:
        """Retain exactly the ordered left- and right-module projections."""
        return (self.to_left(), self.to_right())

    def __call__(
        self,
        left_action: MorphismCategory.ObjectType,
        right_action: MorphismCategory.ObjectType,
    ) -> BimoduleCategory.ObjectType:
        """The bimodule with these two actions; their common codomain is the carrier."""
        assert left_action.codomain() is right_action.codomain(), f"{left_action!r} and {right_action!r} do not act on one carrier"
        return super().__call__(self._pairs((self._left(left_action), self._right(right_action), left_action.codomain())))

    def homomorphism(
        self,
        source: BimoduleCategory.ObjectType,
        target: BimoduleCategory.ObjectType,
        arrow: MorphismCategory.ObjectType,
    ) -> BimoduleCategory.MorphismType:
        """The bimodule morphism over a map of ``V`` preserving both actions; fullness makes it a morphism here."""
        return self.restrict_morphism(self._pairs.homomorphism(source, target, arrow))


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
    pairs = limit_of_categories(cospan_diagram(Cat(), left.forgetful(), right.forgetful()), Cat().Pullbacks(), ActionPairsCategory)
    base, tensor = monoidal.underlying_category(), monoidal.tensor()
    carrier = left.forgetful() * pairs.to_left()
    scalars, co_scalars = left.carrier(), right.carrier()
    associator = monoidal.associator().inverse()
    triples = monoidal.associator().domain().domain()

    def commuting(value: CategoryOfCategories.ElementType, through_the_left: bool) -> MorphismCategory.ObjectType:
        """``lambda (1 (x) rho)`` and ``rho (lambda (x) 1) a^-1`` on ``R (x) (X (x) S)``."""
        x = _retained_object_component(value, 2)
        lam = _retained_object_component(value, 0).action()
        rho = _retained_object_component(value, 1).action()
        match through_the_left:
            case True:
                return lam * tensor_morphism(tensor, Mor(base)(scalars, scalars).one(), rho)
            case False:
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
