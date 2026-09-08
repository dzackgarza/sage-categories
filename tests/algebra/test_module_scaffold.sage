"""Sets with a monoid action as module objects: two scalar actions on one carrier, an equivariant map, restriction of scalars, and transport."""

import pytest

from sage_categories.all import Mor, Sets, Cartesian, SelfAction, ask
from sage_categories.cat.modules import Modules
from sage_categories.cat.structured_objects import Monoids
from sage_categories.cat.calculus import binary_product_data


def conjunction_monoid(carrier):
    """``(carrier, min, 1)``: the Boolean monoid under conjunction, or its square under componentwise conjunction."""
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()
    first = next(iter(carrier)).datum()
    if isinstance(first, tuple):
        operation = Mor(Sets)(square, carrier)(lambda pair: tuple(min(a, b) for a, b in zip(pair[0], pair[1])))
        unit = Mor(Sets)(structure.unit(), carrier)(lambda _: (1, 1))
    else:
        operation = Mor(Sets)(square, carrier)(lambda pair: min(pair))
        unit = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    return Monoids(structure)(operation, unit)


def test_boolean_monoid_acting_on_three_points() -> None:
    structure = Cartesian(Sets())
    actegory = SelfAction(structure)
    booleans = Sets((0, 1))
    scalars = conjunction_monoid(booleans)
    three = Sets((0, 1, 2))
    acted = binary_product_data(Sets(), booleans, three).apex()
    # 1 acts as the identity and 0 sends everything to the sink 2.
    rho = Mor(Sets)(acted, three)(lambda pair: pair[1] if pair[0] == 1 else 2)
    modules = Modules(scalars, actegory)
    module = modules(rho)
    assert module in modules
    assert module.action() is rho
    assert modules.forgetful().on_object(module) is three
    assert module.point(1).parent() is module
    assert module.action()(acted.point((0, 1))).datum() == 2
    assert module.action()(acted.point((1, 1))).datum() == 1

    # 0 acting as the identity and 1 as the sink violates the unit law.
    with pytest.raises(AssertionError):
        modules(Mor(Sets)(acted, three)(lambda pair: pair[1] if pair[0] == 0 else 2))

    # Collapsing 0 and 1 to 0 while fixing the sink is equivariant; sending everything to 1 is not.
    two = Sets((0, 2))
    acted_two = binary_product_data(Sets(), booleans, two).apex()
    target = modules(Mor(Sets)(acted_two, two)(lambda pair: pair[1] if pair[0] == 1 else 2))
    collapse = Mor(Sets)(three, two)(lambda value: 2 if value == 2 else 0)
    equivariant = modules.homomorphism(module, target, collapse)
    assert equivariant in Mor(modules)(module, target)
    assert equivariant(module.point(1)).datum() == 0
    assert modules.forgetful().on_morphism(equivariant) is collapse
    with pytest.raises(AssertionError):
        modules.homomorphism(module, target, Mor(Sets)(three, two)(lambda value: 0))

    # Transport along the bijection exchanging 0 and 2 moves the sink to 0.
    swap = Mor(Sets)(three, three)(lambda value: {0: 2, 1: 1, 2: 0}[value])
    transported = modules.transport(module, swap)
    assert transported.action()(acted.point((0, 1))).datum() == 0
    assert transported.action()(acted.point((1, 1))).datum() == 1
    assert ask(transported == module) is False


def test_two_scalar_actions_on_one_carrier_and_restriction() -> None:
    structure = Cartesian(Sets())
    actegory = SelfAction(structure)
    booleans = Sets((0, 1))
    pairs_carrier = Sets(((0, 0), (0, 1), (1, 0), (1, 1)))
    scalars = conjunction_monoid(pairs_carrier)
    acted = binary_product_data(Sets(), pairs_carrier, booleans).apex()
    by_first = Modules(scalars, actegory)(Mor(Sets)(acted, booleans)(lambda pair: min(pair[0][0], pair[1])))
    by_second = Modules(scalars, actegory)(Mor(Sets)(acted, booleans)(lambda pair: min(pair[0][1], pair[1])))
    assert by_first is not by_second
    assert ask(by_first == by_second) is False
    # The idempotent (1, 0) acts as the identity in one module and as zero in the other.
    assert by_first.action()(acted.point(((1, 0), 1))).datum() == 1
    assert by_second.action()(acted.point(((1, 0), 1))).datum() == 0

    # Restricting scalars along the diagonal monoid morphism b -> (b, b) gives the Boolean action by conjunction on both.
    small = conjunction_monoid(booleans)
    diagonal = Monoids(structure).homomorphism(small, scalars, Mor(Sets)(booleans, pairs_carrier)(lambda value: (value, value)))
    restriction = Modules(scalars, actegory).restriction(diagonal)
    restricted = restriction.on_object(by_second)
    assert restricted in Modules(small, actegory)
    small_acted = binary_product_data(Sets(), booleans, booleans).apex()
    assert restricted.action()(small_acted.point((0, 1))).datum() == 0
    assert restricted.action()(small_acted.point((1, 1))).datum() == 1
    assert Modules(small, actegory).forgetful().on_object(restricted) is booleans


test_boolean_monoid_acting_on_three_points()
test_two_scalar_actions_on_one_carrier_and_restriction()
