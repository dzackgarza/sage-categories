"""``Fun([1], C)`` as morphisms and commuting squares; slices, coslices, and their fibration lifts; the shared-carrier pullback.

Oracles: the definition of the functor category from the walking arrow (an object
is a morphism, a morphism a commuting square ``g * a == b * f``; ``specs/functor.md``,
"The Mor(n, C) tower"); the definition of ``C.SliceOver(x)`` as the pullback of
``ev_1`` along ``x`` and of its membership by ``ask(ev_1(f) == x)`` (POL-CAT-095;
``specs/functor.md``, "Slices and coslices"); the cartesian lift of ``f: y -> x``
at ``p: z -> x`` for ``ev_1`` as the pullback projection ``z *_x y -> y`` (nLab
"codomain fibration"); the cartesian lift of ``f: y -> z`` at ``(z, p)`` for the
slice projection as ``(y, p * f) -> (z, p)`` (nLab "discrete fibration"); a
generalized element of ``x`` as an object of ``C.SliceOver(x)`` (AGENTS.md, "Core
categorical architecture"); the shared-carrier identity precondition (AGENTS.md,
"Universal constructions").  Every equality of finite-set maps is decided by the
finite set-map handler (``specs/sets.md``, "Equality").  No row proves a universal
property or a fibration law (POL-MATH-036).
"""

from dataclasses import dataclass

import pytest

from sage_categories.all import *
from sage_categories.cat.cat_constructions import shared_carrier_pullback
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.kernel.construction import retained_morphism_input, retained_object_input
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory


@dataclass(frozen=True, eq=False, slots=True)
class CarrierData:
    """The local state of an object that carries a set with one piece of extra structure."""

    carrier: object
    structure: object


@dataclass(frozen=True, eq=False, slots=True)
class UnderlyingData:
    """The local state of a morphism that carries one set map."""

    underlying: object


def _forgetful(functor):
    """A faithful functor to ``Sets()`` with the two constructor conversions it must retain."""
    functor.retain_object_constructor_conversion(lambda source: retained_object_input(source.datum.carrier))
    functor.retain_morphism_constructor_conversion(lambda source: retained_morphism_input(source.datum.underlying))
    return functor


class MarkedSets(Category):
    """Sets with a marked point, projecting to ``Sets()`` by the explicit faithful functor ``(X, x) |-> X``."""

    class DeclaredObjectType(ObjectOfCategory):
        def __init__(self, data):
            self._carrier = data.carrier
            self._mark = data.structure
            super().__init__()

        def carrier(self) -> ObjectOfCategory:
            return self._carrier

        def mark(self) -> ElementOfObject:
            return self._mark

    class DeclaredElementType(ElementOfObject):
        """No local operation."""

    class DeclaredMorphismType(MorphismOfCategory):
        def __init__(self, data):
            self._underlying = data.underlying
            super().__init__()

        def underlying(self) -> MorphismOfCategory:
            return self._underlying

    def __init__(self):
        self._functors = {}
        super().__init__()

    def structure_functors(self):
        if "carrier" not in self._functors:
            self._functors["carrier"] = _forgetful(Fun(self, Sets()).Faithful()(lambda marked: marked.carrier(), lambda morphism: morphism.underlying()))
        return (self._functors["carrier"],)

    def __call__(self, carrier, mark):
        assert mark in carrier
        return self.ObjectType(category=self, data=CarrierData(carrier, mark))

    def construct_morphism(self, domain, codomain, underlying):
        return self.MorphismType(category=self.morphism_category(1), domain=domain, codomain=codomain, data=UnderlyingData(underlying))

    def __repr__(self):
        return "MarkedSets"


class SubsetSets(Category):
    """Sets with a chosen subset, projecting to ``Sets()`` by ``(X, A) |-> X``."""

    class DeclaredObjectType(ObjectOfCategory):
        def __init__(self, data):
            self._carrier = data.carrier
            self._chosen = data.structure
            super().__init__()

        def carrier(self) -> ObjectOfCategory:
            return self._carrier

        def chosen(self) -> ObjectOfCategory:
            return self._chosen

    class DeclaredElementType(ElementOfObject):
        """No local operation."""

    class DeclaredMorphismType(MorphismOfCategory):
        def __init__(self, data):
            self._underlying = data.underlying
            super().__init__()

        def underlying(self) -> MorphismOfCategory:
            return self._underlying

    def __init__(self):
        self._functors = {}
        super().__init__()

    def structure_functors(self):
        if "carrier" not in self._functors:
            self._functors["carrier"] = _forgetful(Fun(self, Sets()).Faithful()(lambda subsetted: subsetted.carrier(), lambda morphism: morphism.underlying()))
        return (self._functors["carrier"],)

    def __call__(self, carrier, chosen):
        assert chosen.underlying_set() is carrier
        return self.ObjectType(category=self, data=CarrierData(carrier, chosen))

    def construct_morphism(self, domain, codomain, underlying):
        return self.MorphismType(category=self.morphism_category(1), domain=domain, codomain=codomain, data=UnderlyingData(underlying))

    def __repr__(self):
        return "SubsetSets"


def test_commuting_squares_are_the_morphisms_of_fun_of_the_walking_arrow() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    swap = Mor(Sets())(two, two)(lambda datum: int(1) - datum)
    rotate = Mor(Sets())(three, three)(lambda datum: (datum + int(1)) % int(3))
    arrow = Cat().Simplex(int(1))
    squares = Fun(arrow, Sets())
    ev_0, ev_1 = squares.evaluation(arrow(int(0))), squares.evaluation(arrow(int(1)))

    assert successor in squares
    assert successor in Fun
    assert ev_0(successor) is two and ev_1(successor) is three
    rotated = Mor(Sets())(two, three)(lambda datum: (datum + int(2)) % int(3))
    components = {int(0): swap, int(1): rotate}
    with pytest.raises(AssertionError):
        Mor(squares)(successor, successor)(lambda vertex: components[arrow.label(vertex)])
    double = Mor(Sets())(two, three)(lambda datum: int(2) * datum)
    square = Mor(squares)(successor, double)(lambda vertex: components[arrow.label(vertex)])
    assert square in Mor(squares)
    assert square in Mor(squares)(successor, double)
    assert square.domain() is successor
    assert ev_0.on_morphism(square) is swap
    assert ev_1.on_morphism(square) is rotate
    assert ask(double * swap == rotate * successor) is True
    assert ask(rotated == double * swap) is True


def test_the_slice_is_the_pullback_of_the_codomain_evaluation_along_the_point() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    parity = Mor(Sets())(three, two)(lambda datum: datum % int(2))
    arrow = Cat().Simplex(int(1))
    squares = Fun(arrow, Sets())
    over = Sets().SliceOver(three)

    assert over in Cat()
    assert Sets().SliceOver(three) is over
    assert over.first_functor() is squares.evaluation(arrow(int(1)))
    assert over.second_functor() is Sets().point_functor(three)
    assert over.first_projection().codomain() is squares
    assert over.fixed_projection().domain() is over and over.fixed_projection().codomain() is Sets()

    lifted = over(successor)
    assert lifted in over
    assert over.first_projection().on_object(lifted) is successor
    assert over.fixed_projection().on_object(lifted) is two
    assert successor in over
    assert parity not in over
    other_three = Sets()(lambda datum: datum in (int(0), int(1), int(2)))
    unrelated = Mor(Sets())(two, other_three)(lambda datum: datum)
    assert ask(over.membership_proposition(unrelated)) is Unknown
    assert lifted not in Sets()
    assert ask(over.fixed_projection().on_object(lifted).cardinality() == int(2)) is True

    under = Sets().CosliceUnder(two)
    assert under.first_functor() is squares.evaluation(arrow(int(0)))
    pointed = under(successor)
    assert pointed in under
    assert under.fixed_projection().on_object(pointed) is three
    assert under.first_projection().on_object(pointed) is successor


def test_a_generalized_element_is_an_object_of_the_slice_over_its_parent() -> None:
    three = Sets().Simplex(int(2))
    point = three.point(int(1))
    over = Sets().SliceOver(three)

    assert point.category() is over
    assert point in over
    assert point.defining_morphism().domain() is Sets().Terminal()
    assert point.parent() is three
    assert over(point).first() is point.defining_morphism()
    assert over(point.defining_morphism()) is over(point)
    assert over.fixed_projection().on_object(over(point)) is Sets().Terminal()

    # A stage other than the classical one: ``t: T -> X`` for ``T`` a two-element set.
    two = Sets().Simplex(int(1))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    generalized = Sets().element_from_defining_morphism(successor)
    assert generalized.defining_morphism().domain() is two
    assert generalized.parent() is three
    assert generalized.defining_morphism() is successor
    assert generalized.category() is over
    assert generalized in over
    assert over(generalized).first() is successor
    assert over.fixed_projection().on_object(over(generalized)) is two
    assert generalized is not point


def test_the_codomain_evaluation_lifts_a_map_by_pullback_with_both_projections() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    include = Mor(Sets())(two, three)(lambda datum: datum)
    residue = Mor(Sets())(four, three)(lambda datum: datum % int(3))
    arrow = Cat().Simplex(int(1))
    squares = Fun(arrow, Sets())
    cospan = Cat().Horn(int(2), int(2))
    ev_1 = squares.evaluation(arrow(int(1)))

    lift = ev_1.cartesian_lift(include, residue)
    assert lift in Mor(squares)
    assert lift.codomain() is residue
    lifted = lift.domain()
    assert lifted in Mor(Sets())
    assert lifted.codomain() is two
    to_four = lift.component(arrow(int(0)))
    assert to_four.domain() is lifted.domain() and to_four.codomain() is four
    assert lift.component(arrow(int(1))) is include
    assert ask(residue * to_four == include * lifted) is True
    assert ask(lifted.domain().cardinality() == int(3)) is True
    pullback = lifted.domain()
    assert pullback in Sets().Pullbacks()
    assert pullback.diagram().on_object(cospan(int(0))) is four and pullback.diagram().on_object(cospan(int(1))) is two
    assert lifted is pullback.projection(cospan(int(1)))
    assert to_four is pullback.projection(cospan(int(0)))
    assert ev_1.cartesian_lift(include, residue) is lift


def test_the_slice_projection_lifts_a_map_by_precomposition() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    residue = Mor(Sets())(four, three)(lambda datum: datum % int(3))
    double = Mor(Sets())(two, four)(lambda datum: int(2) * datum)
    over = Sets().SliceOver(three)
    base = over(residue)

    lift = over.fixed_projection().cartesian_lift(double, base)
    assert lift in Mor(over)
    assert lift.codomain() is base
    assert over.fixed_projection().on_morphism(lift) is double
    lifted = lift.domain()
    assert over.fixed_projection().on_object(lifted) is two
    assert ask(lifted.first() == residue * double) is True
    assert ask(lifted.first()(two.point(int(1))) == three.point(int(2))) is True

    under = Sets().CosliceUnder(two)
    pointed = under(double)
    colift = under.fixed_projection().cocartesian_lift(residue, pointed)
    assert colift.domain() is pointed
    assert under.fixed_projection().on_object(colift.codomain()) is three
    assert ask(colift.codomain().first() == residue * double) is True


def test_a_shared_carrier_pullback_accepts_one_carrier_and_rejects_two() -> None:
    marked, subsetted = MarkedSets(), SubsetSets()
    three = Sets().Simplex(int(2))
    other = Sets().Finite()((int(0), int(1), int(2)))
    cospan = Cat().Horn(int(2), int(2))
    combined = shared_carrier_pullback(cospan_diagram(Cat(), marked.selected_functors()[int(0)], subsetted.selected_functors()[int(0)]))

    assert combined in Cat().Pullbacks()
    assert combined.projection(cospan(int(0))).codomain() is marked
    assert combined.projection(cospan(int(1))).codomain() is subsetted
    pair = combined((marked(three, three.point(int(1))), subsetted(three, three.subset_from(lambda datum: datum > int(0)))))
    assert pair in combined
    assert combined.projection(cospan(int(2))).on_object(pair) is three
    assert combined.projection(cospan(int(0))).on_object(pair).mark() is three.point(int(1))
    with pytest.raises(AssertionError):
        combined((marked(three, three.point(int(1))), subsetted(other, other.subset_from(lambda datum: datum > int(0)))))
