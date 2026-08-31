"""R5 acceptance for retained evaluations, pullbacks, and property closure."""

from __future__ import annotations

from sympy.logic.boolalg import Boolean

from sage_categories.cat.category import Cat, ask
from sage_categories.cat.cones import cone, cones, limit_cones
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Fun


def test_r5_1_domain_evaluation_is_the_retained_evaluation_functor():
    walking_arrow = Cat().Simplex(1)
    diagrams = Fun(walking_arrow, Cat())
    evaluation = diagrams.evaluation(walking_arrow(0))
    arrow = Cat().arrow_functor(Cat().point_functor(Cat().Initial()))

    assert evaluation is diagrams.evaluation(walking_arrow(0))
    assert evaluation.on_object(arrow) is arrow.on_object(walking_arrow(0))
    assert evaluation.on_object(arrow) is arrow.on_morphism(walking_arrow.generator("0->1")).domain()


def test_r5_2_fully_faithful_identity_uses_its_exact_proposition_and_same_value():
    endomorphisms = Fun(Cat(), Cat())
    identity = endomorphisms.one()
    fully_faithful = endomorphisms.FullyFaithful()
    proposition = identity.is_fully_faithful()
    identity_before = id(identity)

    assert isinstance(proposition, Boolean)
    assert proposition is fully_faithful.membership_proposition(identity)
    assert ask(proposition) is True
    assert id(identity) == identity_before
    assert identity in fully_faithful


def test_r5_3_terminal_constant_cospan_retains_its_universal_presentation():
    terminal = Cat().Terminal()
    identity = Fun(terminal, terminal).one()
    diagram = cospan_diagram(Cat(), identity, identity)
    pullbacks = Cat().Pullbacks()
    apex = pullbacks(diagram)
    presentation = pullbacks.universal_data(diagram)

    assert apex is terminal
    assert presentation in limit_cones(diagram)
    assert presentation.diagram() is diagram
    assert presentation.apex() is terminal
    assert presentation.leg(0) is identity
    assert presentation.leg(1) is identity

    query_apex = Cat().Simplex(1)
    unique_map = Fun(query_apex, terminal).constant(terminal(0))
    query = cones(diagram)(cone(diagram, query_apex, lambda vertex: unique_map))
    universal_map = presentation.lift(query)

    assert universal_map is unique_map
    assert universal_map in Fun(query_apex, terminal)


def test_r5_4_property_intersection_retains_both_projections_and_ambient_monomorphism():
    fully_faithful = Fun.FullyFaithful()
    equivalences = Fun.Equivalences()
    intersection = fully_faithful.intersection(equivalences)
    diagram = cospan_diagram(
        Cat(),
        fully_faithful.subcategory_monomorphism(),
        equivalences.subcategory_monomorphism(),
    )
    presentation = Cat().Pullbacks().universal_data(diagram)
    first_projection = Fun.full_subcategory_monomorphism(intersection, fully_faithful)
    second_projection = Fun.full_subcategory_monomorphism(intersection, equivalences)
    ambient_monomorphism = intersection.subcategory_monomorphism()

    assert presentation.apex() is intersection
    assert presentation.leg(0) is first_projection
    assert presentation.leg(1) is second_projection
    assert ambient_monomorphism is Fun.full_subcategory_monomorphism(intersection, Fun)
    assert ambient_monomorphism in Fun(intersection, Fun).Monomorphisms().Isofibrations().Full()


def test_r5_5_identity_inverse_image_retains_both_projections_and_ambient_monomorphism():
    identity = Fun(Fun, Fun).one()
    fully_faithful = Fun.FullyFaithful()
    inverse_image = identity.inverse_image(fully_faithful)
    diagram = cospan_diagram(
        Cat(),
        identity,
        fully_faithful.subcategory_monomorphism(),
    )
    presentation = Cat().Pullbacks().universal_data(diagram)
    source_projection = inverse_image.subcategory_monomorphism()
    target_projection = inverse_image.target_projection()

    assert presentation.apex() is inverse_image
    assert presentation.leg(0) is source_projection
    assert presentation.leg(1) is target_projection
    assert source_projection is Fun.full_subcategory_monomorphism(inverse_image, Fun)
    assert source_projection in Fun(inverse_image, Fun).Monomorphisms().Isofibrations().Full()
    assert target_projection in Fun(inverse_image, fully_faithful)


def test_r5_6_results_have_their_exact_semantic_owners():
    walking_arrow = Cat().Simplex(1)
    diagrams = Fun(walking_arrow, Cat())
    evaluation = diagrams.evaluation(walking_arrow(0))
    endomorphisms = Fun(Cat(), Cat())
    identity = endomorphisms.one()
    proposition = identity.is_fully_faithful()

    terminal = Cat().Terminal()
    terminal_identity = Fun(terminal, terminal).one()
    terminal_diagram = cospan_diagram(Cat(), terminal_identity, terminal_identity)
    terminal_apex = Cat().Pullbacks()(terminal_diagram)

    fully_faithful = Fun.FullyFaithful()
    equivalences = Fun.Equivalences()
    intersection = fully_faithful.intersection(equivalences)
    intersection_diagram = cospan_diagram(
        Cat(),
        fully_faithful.subcategory_monomorphism(),
        equivalences.subcategory_monomorphism(),
    )

    identity_on_fun = Fun(Fun, Fun).one()
    inverse_image = identity_on_fun.inverse_image(fully_faithful)
    inverse_diagram = cospan_diagram(
        Cat(),
        identity_on_fun,
        fully_faithful.subcategory_monomorphism(),
    )

    assert evaluation in Fun(diagrams, Cat())
    assert identity in endomorphisms.FullyFaithful()
    assert isinstance(proposition, Boolean)
    assert proposition is endomorphisms.FullyFaithful().membership_proposition(identity)
    assert terminal_apex is Cat().Pullbacks().chosen_object(terminal_diagram)
    assert intersection is Cat().Pullbacks().chosen_object(intersection_diagram)
    assert inverse_image is Cat().Pullbacks().chosen_object(inverse_diagram)


for name, value in tuple(globals().items()):
    if name.startswith("test_"):
        value()
