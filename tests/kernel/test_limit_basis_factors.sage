"""Generic retained equalizer/coequalizer presentation lookup and factor maps."""

from sage_categories.cat.cones import cocone, cone
from sage_categories.cat.functors import Cat
from sage_categories.cat.limit_basis import (
    coequalizer_factor,
    coequalizer_presentation,
    equalizer_factor,
    equalizer_presentation,
    parallel_pair,
)
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.predicates import ask


def test_parallel_pair_presentations_factor_through_their_retained_universal_maps() -> None:
    base = Cat().Simplex(1)
    source, target = base(0), base(1)
    edge = base.generator("0->1")
    source_identity = Mor(base)(source, source).one()
    target_identity = Mor(base)(target, target).one()
    diagram = parallel_pair(edge, edge)
    shape = diagram.domain()
    source_vertex, target_vertex = shape(0), shape(1)

    base.Equalizers().with_universal_data(
        diagram,
        source,
        cone(
            diagram,
            source,
            lambda vertex: source_identity if vertex is source_vertex else edge,
        ),
        lambda candidate: candidate.component(source_vertex),
    )
    equalizer = equalizer_presentation(base, source, source)
    assert equalizer.diagram() is diagram
    assert ask(equalizer.leg(source_vertex) == source_identity) is True
    assert ask(equalizer_factor(equalizer, source_identity) == source_identity) is True

    base.Coequalizers().with_universal_data(
        diagram,
        target,
        cocone(
            diagram,
            target,
            lambda vertex: edge if vertex is source_vertex else target_identity,
        ),
        lambda candidate: candidate.component(target_vertex),
    )
    coequalizer = coequalizer_presentation(base, target_identity)
    assert coequalizer.diagram() is diagram
    assert ask(coequalizer.leg(target_vertex) == target_identity) is True
    assert ask(coequalizer_factor(coequalizer, target_identity) == target_identity) is True


test_parallel_pair_presentations_factor_through_their_retained_universal_maps()
