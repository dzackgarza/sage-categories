"""Native free-group presentations retain relation arrows and universal factors."""

import pytest

from sage_categories.all import Groups, Mor, Sets, Unknown, ask, presented_group


def test_cyclic_two_presentation_retains_relations_and_universal_factor() -> None:
    presentation = presented_group(("a",), ((1, 1),))
    group = presentation.group()
    generator = presentation.generators()[0]

    assert group in Groups(Sets)
    square = group.operation().domain()
    product = group.operation()(square.point((generator.datum(), generator.datum())))
    unit = group.unit_morphism()(group.unit_morphism().domain().an_element())
    assert ask(product == unit) is True
    relation = presentation.relation_images()[0]
    free_generator = presentation.free_generators()[0]
    free_square = presentation.free_group().operation().domain()
    expected_relation = presentation.free_group().operation()(
        free_square.point((free_generator.datum(), free_generator.datum()))
    )
    assert ask(relation == expected_relation) is True
    assert ask(presentation.quotient_morphism()(free_generator) == generator) is True

    target_presentation = presented_group(("b",), ((1, 1, 1, 1),))
    target = target_presentation.group()
    target_generator = target_presentation.evaluate_word((1, 1))
    factor = presentation.factor(target, (target_generator,))
    assert factor in Mor(Groups(Sets))(group, target)
    assert ask(factor(generator) == target_generator) is True


def test_violated_relation_is_rejected_by_the_native_homomorphism_constructor() -> None:
    source = presented_group(("a",), ((1, 1),))
    target_presentation = presented_group(("b",))
    free_target = target_presentation.group()
    with pytest.raises(ValueError):
        source.factor(free_target, (target_presentation.generators()[0],))


def test_free_group_carrier_is_rule_defined_not_enumerated() -> None:
    presentation = presented_group(("x", "y"))
    free = presentation.group()
    assert Sets.chosen_enumeration(free.operation().codomain()) is Unknown
    assert ask(presentation.evaluate_word((1, 2)) == presentation.evaluate_word((2, 1))) is False
    first = presentation.evaluate_word((1,))
    inverse_second = presentation.evaluate_word((-2,))
    assert presentation.evaluate_word((1, -2)).datum() == first.datum() * inverse_second.datum()
    with pytest.raises(ValueError):
        presentation.evaluate_word((3,))


test_cyclic_two_presentation_retains_relations_and_universal_factor()
test_violated_relation_is_rejected_by_the_native_homomorphism_constructor()
test_free_group_carrier_is_rule_defined_not_enumerated()
