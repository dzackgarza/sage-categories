"""Bimodules over M_2(F_2): the regular bimodule, whose left and right actions differ, and a two-sided map."""

from sage_categories.all import ask
from sage_categories.algebra import AbelianTensor, abelian_homomorphism, integer_group, presented_abelian_group, simple_tensor, tensor_mediator
from sage_categories.cat.bimodules import Bimodules
from sage_categories.cat.monoidal import Reversed
from sage_categories.cat.structured_objects import Monoids


def matrix_ring():
    """``M_2(F_2)`` on ``(Z/2)^4`` in the entry order ``(a11, a12, a21, a22)``, with its two monoid readings."""
    engine = AdditiveAbelianGroup([2, 2, 2, 2])
    entries = lambda datum: [int(c) for c in datum.vector()]
    element = lambda values: engine.linear_combination_of_smith_form_gens(vector(ZZ, values))

    def multiply(a, b):
        x, y = entries(a), entries(b)
        return element([
            x[0] * y[0] + x[1] * y[2], x[0] * y[1] + x[1] * y[3],
            x[2] * y[0] + x[3] * y[2], x[2] * y[1] + x[3] * y[3],
        ])

    group = presented_abelian_group(engine)
    operation = tensor_mediator(group, group, group, multiply)
    unit = abelian_homomorphism(integer_group(), group, lambda k: k * element([1, 0, 0, 1]))
    # The same multiplication and unit present S in V and the opposite monoid in V^rev.
    return element, group, operation, Monoids(AbelianTensor())(operation, unit), Monoids(Reversed(AbelianTensor()))(operation, unit)


def test_the_regular_bimodule_of_a_noncommutative_ring_keeps_its_two_actions_apart() -> None:
    element, group, operation, ring, opposite = matrix_ring()
    bimodules = Bimodules(ring, opposite, AbelianTensor())
    regular = bimodules(operation, operation)
    assert regular in bimodules
    assert bimodules.forgetful().on_object(regular) is group
    assert bimodules.to_left().on_object(regular) in bimodules.left_modules()
    assert bimodules.to_right().on_object(regular) in bimodules.right_modules()

    e12, e21 = element([0, 1, 0, 0]), element([0, 0, 1, 0])
    # ``a x`` through the left action and ``x a`` through the right action, at the same scalar ``a``.
    on_the_left = lambda a, x: regular.left_action()(simple_tensor(group, group, a, x))
    on_the_right = lambda a, x: regular.right_action()(simple_tensor(group, group, x, a))

    # E12 E21 = E11 while E21 E12 = E22, so acting by E12 on the left of E21 is not
    # acting by E12 on its right.
    assert ask(on_the_left(e12, e21) == group.point(element([1, 0, 0, 0]))) is True
    assert ask(on_the_right(e12, e21) == group.point(element([0, 0, 0, 1]))) is True
    assert ask(on_the_left(e12, e21) == on_the_right(e12, e21)) is False

    # The commuting law the category imposes, read on elements: (E12 E21) E12 = E12 (E21 E12).
    assert ask(on_the_right(e12, on_the_left(e12, e21).datum()) == on_the_left(e12, on_the_right(e12, e21).datum())) is True
    assert ask(on_the_left(e12, on_the_right(e12, e21).datum()) == group.point(e12)) is True


def test_a_two_sided_map_of_bimodules_is_a_morphism_and_a_one_sided_map_is_not() -> None:
    element, group, operation, ring, opposite = matrix_ring()
    bimodules = Bimodules(ring, opposite, AbelianTensor())
    regular = bimodules(operation, operation)

    # Left multiplication by the identity is two-sided; the two structures make it a morphism.
    identity = abelian_homomorphism(group, group, lambda x: x)
    arrow = bimodules.homomorphism(regular, regular, identity)
    assert arrow in bimodules.morphism_category(1)(regular, regular)
    assert ask(bimodules.forgetful().on_morphism(arrow) == identity) is True

    # Transposition preserves the additive group but exchanges the two actions, so it is
    # not a bimodule morphism from the regular bimodule to itself.
    entries = lambda datum: [int(c) for c in datum.vector()]
    transpose = abelian_homomorphism(group, group, lambda x: element([entries(x)[0], entries(x)[2], entries(x)[1], entries(x)[3]]))
    rejected = False
    try:
        bimodules.homomorphism(regular, regular, transpose)
    except AssertionError:
        rejected = True
    assert rejected, "transposition exchanges the two actions, so it is not a morphism of the regular bimodule"


test_the_regular_bimodule_of_a_noncommutative_ring_keeps_its_two_actions_apart()
test_a_two_sided_map_of_bimodules_is_a_morphism_and_a_one_sided_map_is_not()
