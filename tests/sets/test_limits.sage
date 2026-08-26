"""``Sets()`` limits and colimits over non-discrete shapes: compatible families and quotients.

Oracles: the limit of a diagram of sets is the set of compatible families (Mathlib
``Limits.Types.limitCone``: the sections ``s`` with ``F.map f (s j) = s j'``); the
colimit is the quotient of the disjoint union by the equivalence relation generated
by ``(j, x) ~ (j', F.map f x)`` (Mathlib ``Functor.ColimitTypeRel``, ``Relation.EqvGen``);
the pullback of ``[1] -> [2] <- [3]`` with ``d |-> d`` and ``d |-> d mod 3`` has the
three pairs ``(0, 0)``, ``(1, 1)``, ``(0, 3)`` by direct computation; the equalizer of
``d mod 2`` and ``0`` on ``{0, 1, 2}`` is ``{0, 2}`` and their coequalizer identifies
``1`` with ``0``, leaving one class (``specs/sets.md``, "General limits and colimits");
the mediator equations are decided by the finite set-map equality handler
(``specs/sets.md``, "Equality").  No row proves a universal property (POL-MATH-036).
"""

import pytest

from sage_categories.all import *
from sage_categories.cat.constructions import cocone, cone
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.shapes import omega


def _fold(images, path):
    if not path.word():
        return images["identity"](path.domain())
    first, *rest = path.word()
    image = images[first]
    for name in rest:
        image = images[name] * image
    return image


def _sequence(stage_sets, transitions):
    """A diagram over ``omega`` from a rule ``n |-> X_n`` and a rule ``(m, n) |-> X_m -> X_n``."""
    shape = omega()

    def on_object(vertex):
        return stage_sets(vertex.point())

    def on_morphism(comparison):
        return transitions(comparison.domain().point(), comparison.codomain().point())

    return Fun(shape, Sets())(on_object, on_morphism)


def _simplex_sequence():
    """The sequence ``[0] -> [1] -> [2] -> ...`` of inclusions ``d |-> d``."""
    return _sequence(lambda point: Sets().Simplex(int(point._datum) - int(1)), lambda lower, upper: Mor(Sets())(Sets().Simplex(int(lower._datum) - int(1)), Sets().Simplex(int(upper._datum) - int(1)))(lambda datum: datum))


def test_set_limit_membership_is_the_compatibility_decision() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    include = Mor(Sets())(two, three)(lambda datum: datum)
    residue = Mor(Sets())(four, three)(lambda datum: datum % int(3))
    cospan = Cat().Horn(int(2), int(2))
    pullback = Sets().Pullbacks()(cospan_diagram(Sets(), include, residue))
    first, second = pullback.projection(cospan(int(0))), pullback.projection(cospan(int(1)))

    assert pullback in Sets().Limits(cospan)
    assert pullback in Sets().Finite()
    assert ask(pullback.cardinality() == int(3)) is True
    members = list(pullback)
    assert all(ask(include(first(member)) == residue(second(member))) is True for member in members)
    assert any(ask(second(member) == four.point(int(3))) is True for member in members)
    assert pullback in Sets()
    assert pullback in Sets().ChosenSubsets()
    product = pullback.underlying_set()
    assert pullback.inclusion() in Mor(Sets())(pullback, product).Monomorphisms()
    assert product in Sets().Products()
    assert ask(product.cardinality() == int(24)) is True
    rejected = [point for point in product if point not in pullback]
    assert len(rejected) == int(21)
    assert all(ask(pullback.membership_proposition(point)) is False for point in rejected)

    increment = Mor(Sets())(NN, NN)(lambda datum: datum + int(1))
    increment_again = Mor(Sets())(NN, NN)(lambda datum: datum + int(1))
    name, name_again = Sets().name_of(increment).defining_morphism(), Sets().name_of(increment_again).defining_morphism()
    undecided = Sets().Pullbacks()(cospan_diagram(Sets(), name, name_again))
    one = Sets().Terminal()
    families = undecided.underlying_set()
    legs = {int(0): one.identity(), int(1): one.identity(), int(2): name}
    into_families = families.universal_morphism(cone(families.diagram(), one, lambda vertex: legs[cospan.label(cospan.object_at(vertex.point()))]))
    corner = into_families(one.point(()))
    assert ask(undecided.membership_proposition(corner)) is Unknown
    assert corner not in undecided
    assert undecided.cardinality() is Unknown


def test_mediator_equations_hold_on_a_finite_cone_and_a_non_cone_is_rejected() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    include = Mor(Sets())(two, three)(lambda datum: datum)
    residue = Mor(Sets())(four, three)(lambda datum: datum % int(3))
    cospan = Cat().Horn(int(2), int(2))
    pullback = Sets().Pullbacks()(cospan_diagram(Sets(), include, residue))
    diagram = pullback.diagram()
    parity = Mor(Sets())(four, two)(lambda datum: datum % int(2))
    fold = Mor(Sets())(four, four)(lambda datum: datum % int(2))
    flip = Mor(Sets())(four, four)(lambda datum: int(3) - datum)
    legs = {int(0): parity, int(1): fold, int(2): include * parity}
    candidate = cone(diagram, four, lambda vertex: legs[cospan.label(vertex)])

    mediating = pullback.universal_morphism(candidate)
    assert mediating in Mor(Sets())(four, pullback)
    assert ask(pullback.projection(cospan(int(0))) * mediating == parity) is True
    assert ask(pullback.projection(cospan(int(1))) * mediating == fold) is True
    assert ask(pullback.projection(cospan(int(1))) * mediating == flip) is False
    assert mediating(four.point(int(3))) in pullback
    assert ask(pullback.projection(cospan(int(1)))(mediating(four.point(int(3)))) == four.point(int(1))) is True

    twisted = {int(0): parity, int(1): Mor(Sets())(four, four)(lambda datum: datum), int(2): include * parity}
    with pytest.raises(AssertionError):
        pullback.universal_morphism(cone(diagram, four, lambda vertex: twisted[cospan.label(vertex)]))


def test_the_limit_functor_maps_a_natural_transformation_to_the_induced_morphism_of_pullbacks() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    include = Mor(Sets())(two, three)(lambda datum: datum)
    residue = Mor(Sets())(four, three)(lambda datum: datum % int(3))
    shift = Mor(Sets())(three, four)(lambda datum: datum + int(1))
    project = Mor(Sets())(four, four)(lambda datum: (datum % int(3)) + int(1))
    cospan = Cat().Horn(int(2), int(2))
    source, target = Sets().Pullbacks()(cospan_diagram(Sets(), include, residue)), Sets().Pullbacks()(cospan_diagram(Sets(), shift, project))
    components = {int(0): Mor(Sets())(two, three)(lambda datum: datum), int(1): Mor(Sets())(four, four)(lambda datum: datum), int(2): shift}
    transformation = Mor(Fun(cospan, Sets()))(source.diagram(), target.diagram())(lambda vertex: components[cospan.label(vertex)])
    limit = Sets().Limits(cospan).limit_functor()

    assert limit in Fun(Fun(cospan, Sets()), Sets())
    assert limit.on_object(source.diagram()) is source
    induced = limit.on_morphism(transformation)
    assert induced in Mor(Sets())(source, target)
    for vertex in (cospan(int(0)), cospan(int(1))):
        assert ask(target.projection(vertex) * induced == transformation.component(vertex) * source.projection(vertex)) is True


def test_set_colimit_equality_over_omega_is_agreement_at_the_larger_stage() -> None:
    shape = omega()
    sequence = _sequence(lambda point: NN, lambda lower, upper: Mor(Sets())(NN, NN)(lambda datum: datum + (upper._datum - lower._datum)))
    colimit = Sets().Colimits(shape)(sequence)
    first, third = colimit.injection(shape(NN(int(1)))), colimit.injection(shape(NN(int(3))))

    assert colimit in Sets().Colimits(shape)
    assert colimit in Sets().ChosenQuotients()
    assert colimit.quotient_map() in Mor(Sets())(colimit.underlying_set(), colimit).Epimorphisms()
    assert colimit.underlying_set() in Sets().Coproducts()
    assert colimit.cocone() in Mor(Fun(shape, Sets()))
    assert ask(first(NN(int(5))) == third(NN(int(7)))) is True
    assert ask(first(NN(int(5))) == third(NN(int(8)))) is Unknown
    assert ask(third(NN(int(7))) == first(NN(int(5)))) is True
    assert colimit.cardinality() is Unknown

    descend = cocone(sequence, ZZ, lambda vertex: Mor(Sets())(NN, ZZ)(lambda datum: datum - vertex.point()._datum))
    mediating = colimit.universal_morphism(descend)
    assert mediating in Mor(Sets())(colimit, ZZ)
    assert ask(mediating(third(NN(int(7)))) == ZZ(int(4))) is True
    assert ask(mediating(first(NN(int(5)))) == ZZ(int(4))) is True


def test_the_colimit_functor_maps_a_natural_transformation_between_sequences() -> None:
    shape = omega()
    source = _simplex_sequence()
    target = _sequence(lambda point: Sets().Simplex(int(point._datum)), lambda lower, upper: Mor(Sets())(Sets().Simplex(int(lower._datum)), Sets().Simplex(int(upper._datum)))(lambda datum: datum))
    successor = Mor(Fun(shape, Sets()))(source, target)(lambda vertex: Mor(Sets())(source.on_object(vertex), target.on_object(vertex))(lambda datum: datum + int(1)))
    colimit = Sets().Colimits(shape).colimit_functor()
    lower, upper = Sets().Colimits(shape)(source), Sets().Colimits(shape)(target)

    assert colimit.on_object(source) is lower
    induced = colimit.on_morphism(successor)
    assert induced in Mor(Sets())(lower, upper)
    for stage in (shape(NN(int(2))), shape(NN(int(3)))):
        assert ask(induced * lower.injection(stage) == upper.injection(stage) * successor.component(stage)) is True
    assert ask(induced(lower.injection(shape(NN(int(2))))(Sets().Simplex(int(1)).point(int(1)))) == upper.injection(shape(NN(int(4))))(Sets().Simplex(int(4)).point(int(2)))) is True


def test_shape_indexed_limit_families_are_distinct_and_retain_their_universal_data() -> None:
    cospan, shape = Cat().Horn(int(2), int(2)), omega()
    assert Sets().Limits(cospan) is not Sets().Colimits(shape)
    assert Sets().Limits(cospan) is Sets().Pullbacks()
    assert Sets().Colimits(Cat().Horn(int(2), int(0))) is Sets().Pushouts()

    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    include = Mor(Sets())(two, three)(lambda datum: datum)
    pullback = Sets().Pullbacks()(cospan_diagram(Sets(), include, include))
    lift = Fun(Cat().Simplex(int(1)), Sets()).cartesian_lift(include, include)
    assert lift.domain().domain() is pullback
    assert pullback.cone() in Mor(Fun(cospan, Sets()))
    assert pullback.projection(cospan(int(0))).domain() is pullback
    assert pullback.projection(cospan(int(1))).codomain() is two
    assert ask(pullback.cardinality() == int(2)) is True

    sequence = _simplex_sequence()
    colimit = Sets().Colimits(shape)(sequence)
    assert colimit.injection(shape(NN(int(2)))).domain() is Sets().Simplex(int(1))
    assert colimit.injection(shape(NN(int(2)))).codomain() is colimit
    assert colimit.cardinality() is Unknown

    one = Sets().Terminal()
    limit = Sets().Limits(shape)(sequence)
    assert limit.cone() in Mor(Fun(shape, Sets()))
    assert limit.projection(shape(NN(int(3)))).codomain() is Sets().Simplex(int(2))
    assert limit.cardinality() is Unknown
    select_zero = cone(sequence, one, lambda vertex: Mor(Sets())(one, sequence.on_object(vertex))(lambda star: int(0)))
    mediating = limit.universal_morphism(select_zero)
    assert mediating in Mor(Sets())(one, limit)
    assert ask(limit.projection(shape(NN(int(3)))) * mediating == select_zero.component(shape(NN(int(3))))) is True
    assert ask(limit.projection(shape(NN(int(3))))(mediating(one.point(()))) == Sets().Simplex(int(2)).point(int(0))) is True
    families = limit.underlying_set()
    into_families = families.universal_morphism(cone(families.diagram(), one, lambda vertex: select_zero.component(shape.object_at(vertex.point()))))
    assert ask(limit.membership_proposition(into_families(one.point(())))) is Unknown


def test_equalizers_coequalizers_and_pushouts_are_the_constructions_at_their_shapes() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    parity = Mor(Sets())(three, two)(lambda datum: datum % int(2))
    zero = Mor(Sets())(three, two)(lambda datum: int(0))
    pair = Cat().WalkingParallelPair()
    objects = {int(0): three, int(1): two}
    images = {"identity": lambda vertex: objects[pair.label(vertex)].identity(), "f": parity, "g": zero}
    diagram = Fun(pair, Sets())(lambda vertex: objects[pair.label(vertex)], lambda path: _fold(images, path))

    equalizer = Sets().Equalizers()(diagram)
    assert ask(equalizer.cardinality() == int(2)) is True
    members = list(equalizer)
    assert all(ask(parity(equalizer.projection(pair(int(0)))(member)) == zero(equalizer.projection(pair(int(0)))(member))) is True for member in members)
    assert all(ask(equalizer.projection(pair(int(0)))(member) == three.point(int(1))) is False for member in members)

    coequalizer = Sets().Coequalizers()(diagram)
    assert ask(coequalizer.cardinality() == int(1)) is True
    assert ask(coequalizer.injection(pair(int(1)))(two.point(int(0))) == coequalizer.injection(pair(int(1)))(two.point(int(1)))) is True

    span = Cat().Horn(int(2), int(0))
    one = Sets().Terminal()
    select_zero, select_one = Mor(Sets())(one, two)(lambda star: int(0)), Mor(Sets())(one, three)(lambda star: int(1))
    legs = {int(0): one, int(1): two, int(2): three}
    span_images = {"identity": lambda vertex: legs[span.label(vertex)].identity(), "0->1": select_zero, "0->2": select_one}
    pushout = Sets().Pushouts()(Fun(span, Sets())(lambda vertex: legs[span.label(vertex)], lambda path: _fold(span_images, path)))
    assert ask(pushout.cardinality() == int(4)) is True
    assert ask(pushout.injection(span(int(1)))(two.point(int(0))) == pushout.injection(span(int(2)))(three.point(int(1)))) is True
    assert ask(pushout.injection(span(int(1)))(two.point(int(1))) == pushout.injection(span(int(2)))(three.point(int(1)))) is False


def test_an_image_is_the_chosen_subset_of_points_with_a_preimage() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    residue = Mor(Sets())(four, three)(lambda datum: datum % int(3))
    collapse = Mor(Sets())(four, three)(lambda datum: min(datum, int(1)))
    image, collapsed = residue.image(), collapse.image()

    assert image in Sets().Finite()
    assert ask(image.cardinality() == int(3)) is True
    assert ask(collapsed.cardinality() == int(2)) is True
    assert collapsed.inclusion() in Mor(Sets())(collapsed, three).Monomorphisms()
    assert collapsed.underlying_set() is three
    assert three.point(int(1)) in collapsed
    assert three.point(int(2)) not in collapsed
    assert residue.image() is image

    include = Mor(Sets())(two, three)(lambda datum: datum)
    assert ask(include.is_monomorphism()) is True
    assert include.image().cardinality() is two.cardinality()

    shift = Mor(Sets())(ZZ, ZZ).Monomorphisms()(lambda datum: datum + int(1))
    shifted = shift.image()
    assert shifted.cardinality() is ZZ.cardinality()
    assert shifted in Sets().Countable()
    assert ask(shifted.membership_proposition(ZZ(int(3)))) is Unknown
    assert ask(shifted.membership_proposition(QQ(int(1) / int(2)))) is False
