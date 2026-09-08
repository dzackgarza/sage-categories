"""Relative tensor over a noncommutative ring, its coherence maps, and monoid objects in its bimodule category."""

from sage_categories.all import ask
from sage_categories.algebra import (
    AbelianBimoduleTensor,
    AbelianTensor,
    abelian_homomorphism,
    balanced_tensor,
    integer_group,
    presented_abelian_group,
    relative_tensor,
    relative_tensor_mediator,
    tensor_mediator,
)
from sage_categories.cat.monoidal import tensor_object
from sage_categories.cat.structured_objects import Magmas, Monoids


def matrix_ring():
    """``M_2(F_2)`` in the entry order ``(a11, a12, a21, a22)``."""
    engine = AdditiveAbelianGroup([2, 2, 2, 2])
    entries = lambda datum: [int(entry) for entry in datum.vector()]
    element = lambda values: engine.linear_combination_of_smith_form_gens(vector(ZZ, values))

    def multiply(left, right):
        x, y = entries(left), entries(right)
        return element([
            x[0] * y[0] + x[1] * y[2], x[0] * y[1] + x[1] * y[3],
            x[2] * y[0] + x[3] * y[2], x[2] * y[1] + x[3] * y[3],
        ])

    group = presented_abelian_group(engine)
    multiplication = tensor_mediator(group, group, group, multiply)
    identity = element([1, 0, 0, 1])
    unit = abelian_homomorphism(integer_group(), group, lambda value: value * identity)
    return entries, element, multiply, group, Monoids(AbelianTensor())(multiplication, unit)


def test_relative_tensor_supplies_coherence_and_a_nonidentity_algebra_map() -> None:
    entries, element, multiply, ring_group, ring = matrix_ring()
    structure = AbelianBimoduleTensor(ring)
    bimodules = structure.underlying_category()

    pair_engine = AdditiveAbelianGroup([2] * 8)
    pair_group = presented_abelian_group(pair_engine)

    def pair_element(first, second):
        return pair_engine.linear_combination_of_smith_form_gens(
            vector(ZZ, [*entries(first), *entries(second)])
        )

    def pair_components(value):
        coordinates = [int(entry) for entry in value.vector()]
        return element(coordinates[:4]), element(coordinates[4:])

    def act_on_the_left(scalar, value):
        first, second = pair_components(value)
        return pair_element(multiply(scalar, first), multiply(scalar, second))

    def act_on_the_right(value, scalar):
        first, second = pair_components(value)
        return pair_element(multiply(first, scalar), multiply(second, scalar))

    pair_bimodule = bimodules(
        tensor_mediator(ring_group, pair_group, pair_group, act_on_the_left),
        tensor_mediator(pair_group, ring_group, pair_group, act_on_the_right),
    )
    projection = relative_tensor(pair_bimodule.right_action(), pair_bimodule.left_action())

    def componentwise_product(left, right):
        left_first, left_second = pair_components(left)
        right_first, right_second = pair_components(right)
        return pair_element(
            multiply(left_first, right_first),
            multiply(left_second, right_second),
        )

    underlying_multiplication = relative_tensor_mediator(
        projection,
        pair_group,
        componentwise_product,
    )
    tensor_square = tensor_object(structure.tensor(), pair_bimodule, pair_bimodule)
    multiplication = bimodules.homomorphism(
        tensor_square,
        pair_bimodule,
        underlying_multiplication,
    )
    magma = Magmas(structure).algebra(pair_bimodule, multiplication)

    diagonal = abelian_homomorphism(
        ring_group,
        pair_group,
        lambda value: pair_element(value, value),
    )
    unit = bimodules.homomorphism(structure.unit(), pair_bimodule, diagonal)
    monoids = Monoids(structure)
    algebra = monoids(multiplication, unit)

    e12 = element([0, 1, 0, 0])
    e21 = element([0, 0, 1, 0])
    e11 = element([1, 0, 0, 0])
    e22 = element([0, 0, 0, 1])
    left = pair_element(e12, e21)
    right = pair_element(e21, e12)
    product = bimodules.forgetful().on_morphism(magma.operation())(
        balanced_tensor(projection, left, right)
    )
    assert ask(product == pair_group.point(pair_element(e11, e22))) is True

    swap = abelian_homomorphism(
        pair_group,
        pair_group,
        lambda value: pair_element(*reversed(pair_components(value))),
    )
    bimodule_swap = bimodules.homomorphism(pair_bimodule, pair_bimodule, swap)
    algebra_swap = monoids.homomorphism(algebra, algebra, bimodule_swap)
    through_magmas = monoids.to_magmas().on_morphism(algebra_swap)
    through_bimodules = Magmas(structure).forgetful().on_morphism(through_magmas)
    underlying_swap = bimodules.forgetful().on_morphism(through_bimodules)
    source = pair_group.point(pair_element(e12, e21))
    assert ask(underlying_swap(source) == pair_group.point(pair_element(e21, e12))) is True
    assert ask(underlying_swap(source) == source) is False

    regular = structure.unit()
    assert ask(structure.triangle(pair_bimodule, regular)) is True
    assert ask(structure.pentagon(regular, regular, regular, regular)) is True


test_relative_tensor_supplies_coherence_and_a_nonidentity_algebra_map()
