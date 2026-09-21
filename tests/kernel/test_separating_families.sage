"""Restricted Yoneda and separating-family evaluation on nonenumerable probe Homs."""

from sympy import Q

from sage_categories.all import Cat, Fun, Mor, NN, Sets, ask, assume
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.shapes import Discrete
from sage_categories.cat.weighted import separating_evaluation_injection


def test_restricted_yoneda_and_separating_evaluation_are_nonenumerative():
    probes = Discrete(NN)
    terminal = Sets.Terminal()
    test = Fun(probes, Sets).constant(terminal)
    pairs = Cat().Products()((Sets.op(), Sets))

    def hom_at(pair):
        source = pair.family_component(0)
        target = pair.family_component(1)
        homs = Mor(Sets)(source, target)
        return Sets.from_membership(homs.membership_proposition)

    def hom_on_morphism(arrow):
        source = probe_hom.on_object(arrow.domain())
        target = probe_hom.on_object(arrow.codomain())
        return Mor(Sets)(source, target)(
            lambda candidate: arrow.family_component(1)
            * candidate
            * opposite_morphism(arrow.family_component(0))
        )

    probe_hom = Fun(pairs, Sets)(hom_at, hom_on_morphism)
    nerve = test.restricted_yoneda(probe_hom)
    assert nerve.domain() is Sets
    assert nerve.codomain() is Fun(probes.op(), Sets)

    integers = Sets.from_membership(Q.integer)
    shift = Mor(Sets)(integers, integers)(lambda value: value + 1)
    probe_point = NN.point(101)
    probe = probes.object_at(probe_point)
    chosen = Mor(Sets)(terminal, integers)(lambda value: 5)
    hom_set = nerve.on_object(integers).on_object(probe)
    chosen_point = hom_set.point(chosen)
    transported_point = nerve.on_morphism(shift).component(probe)(chosen_point)
    assert ask(transported_point.datum() == shift * chosen) is True

    assume(nerve.is_faithful())
    evaluation = test.separating_evaluation(probe_hom)
    source = evaluation.domain()
    assert evaluation.codomain() is Fun(Sets, Sets).one()
    assert evaluation.component(integers) in Mor(Sets).Epimorphisms()

    injection = separating_evaluation_injection(
        test,
        probe_hom,
        integers,
        probe_point,
        chosen_point,
    )
    terminal_point = next(iter(terminal))
    injected = injection(terminal_point)
    assert evaluation.component(integers)(injected).datum() == chosen(terminal_point).datum()

    transported_injection = separating_evaluation_injection(
        test,
        probe_hom,
        integers,
        probe_point,
        transported_point,
    )
    induced = source.on_morphism(shift)
    transported = induced(injected)
    expected = transported_injection(terminal_point)
    assert evaluation.component(integers)(transported).datum() == evaluation.component(integers)(expected).datum()
    assert (shift * evaluation.component(integers))(injected).datum() == (
        evaluation.component(integers) * induced
    )(injected).datum()


test_restricted_yoneda_and_separating_evaluation_are_nonenumerative()
