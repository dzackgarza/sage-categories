"""Decisive commutative- and noncommutative-base consumers of the relative algebra owner."""

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ

from sage_categories.algebra.abelian import (
    AbelianBimoduleTensor,
    AbelianTensor,
    abelian_homomorphism,
    balanced_tensor,
    integer_group,
    presented_abelian_group,
    relative_tensor,
    relative_tensor_mediator,
    simple_tensor,
    tensor_mediator,
)
from sage_categories.algebra.algebras import Algebras
from sage_categories.cat.category import ask
from sage_categories.cat.monoidal import tensor_object
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import Monoids


def prime_field_five():
    """``F_5`` as a monoid object of ``(Ab, tensor)``."""
    engine = AdditiveAbelianGroup([5])
    group = presented_abelian_group(engine)
    element = lambda value: engine.linear_combination_of_smith_form_gens(
        vector(ZZ, [value])
    )
    multiplication = tensor_mediator(
        group,
        group,
        group,
        lambda left, right: int(left.vector()[0]) * right,
    )
    unit = abelian_homomorphism(
        integer_group(), group, lambda value: value * element(1)
    )
    return element, group, Monoids(AbelianTensor())(multiplication, unit)


def matrix_ring():
    """``M_2(F_2)`` in row-major order as a monoid object of ``(Ab, tensor)``."""
    engine = AdditiveAbelianGroup([2, 2, 2, 2])
    entries = lambda datum: [int(entry) for entry in datum.vector()]
    element = lambda values: engine.linear_combination_of_smith_form_gens(
        vector(ZZ, values)
    )

    def multiply(left, right):
        x, y = entries(left), entries(right)
        return element(
            [
                x[0] * y[0] + x[1] * y[2],
                x[0] * y[1] + x[1] * y[3],
                x[2] * y[0] + x[3] * y[2],
                x[2] * y[1] + x[3] * y[3],
            ]
        )

    group = presented_abelian_group(engine)
    multiplication = tensor_mediator(group, group, group, multiply)
    identity = element([1, 0, 0, 1])
    unit = abelian_homomorphism(integer_group(), group, lambda value: value * identity)
    return (
        entries,
        element,
        multiply,
        group,
        Monoids(AbelianTensor())(multiplication, unit),
    )


def test_dual_numbers_are_recovered_through_the_relative_algebra_presentation() -> None:
    field_element, field_group, field = prime_field_five()
    structure = AbelianBimoduleTensor(field)
    bimodules = structure.underlying_category()
    modules = bimodules.left_modules()

    engine = AdditiveAbelianGroup([5, 5])
    group = presented_abelian_group(engine)
    element = lambda first, second: engine.linear_combination_of_smith_form_gens(
        vector(ZZ, [first, second])
    )

    def coordinates(value):
        return tuple(int(entry) for entry in value.vector())

    def left_scale(scalar, value):
        coefficient = int(scalar.vector()[0])
        first, second = coordinates(value)
        return element(coefficient * first, coefficient * second)

    def right_scale(value, scalar):
        return left_scale(scalar, value)

    dual = bimodules(
        tensor_mediator(field_group, group, group, left_scale),
        tensor_mediator(group, field_group, group, right_scale),
    )
    projection = relative_tensor(dual.right_action(), dual.left_action())

    def multiply(left, right):
        first, epsilon = coordinates(left)
        second, delta = coordinates(right)
        return element(first * second, first * delta + epsilon * second)

    underlying_multiplication = relative_tensor_mediator(projection, group, multiply)
    tensor_square = tensor_object(structure.tensor(), dual, dual)
    multiplication = bimodules.homomorphism(
        tensor_square,
        dual,
        underlying_multiplication,
    )
    underlying_unit = abelian_homomorphism(
        field_group,
        group,
        lambda value: element(int(value.vector()[0]), 0),
    )
    unit = bimodules.homomorphism(structure.unit(), dual, underlying_unit)

    neutral = Monoids(structure)(multiplication, unit)
    algebras = Algebras(field, structure)
    algebra = algebras.from_monoid(neutral)
    presentation = algebras.monoid_presentation()

    assert algebras.base() is field
    assert presentation.on_object(algebra) is neutral
    assert presentation.inverse().on_object(neutral) is algebra

    left_multiplication = bimodules.to_left().on_morphism(multiplication)
    left_unit = bimodules.to_left().on_morphism(unit)
    assert left_multiplication in Mor(modules)(
        bimodules.to_left().on_object(tensor_square),
        bimodules.to_left().on_object(dual),
    )
    assert left_unit in Mor(modules)(
        bimodules.to_left().on_object(structure.unit()),
        bimodules.to_left().on_object(dual),
    )

    epsilon = element(0, 1)
    epsilon_square = bimodules.forgetful().on_morphism(multiplication)(
        balanced_tensor(projection, epsilon, epsilon)
    )
    assert ask(epsilon_square == group.zero()) is True

    scale_epsilon = abelian_homomorphism(
        group,
        group,
        lambda value: element(coordinates(value)[0], 2 * coordinates(value)[1]),
    )
    bimodule_map = bimodules.homomorphism(dual, dual, scale_epsilon)
    automorphism = algebras.homomorphism(algebra, algebra, bimodule_map)
    inverse_scale_epsilon = abelian_homomorphism(
        group,
        group,
        lambda value: element(coordinates(value)[0], 3 * coordinates(value)[1]),
    )
    inverse_bimodule_map = bimodules.homomorphism(dual, dual, inverse_scale_epsilon)
    inverse_automorphism = algebras.homomorphism(
        algebra,
        algebra,
        inverse_bimodule_map,
    )
    identity = Mor(algebras)(algebra, algebra).one()
    assert ask(automorphism * inverse_automorphism == identity) is True
    assert ask(inverse_automorphism * automorphism == identity) is True
    algebras.retain_inverses(automorphism, inverse_automorphism)
    assert automorphism in Mor(algebras).Isomorphisms()
    recovered = presentation.inverse().on_morphism(
        presentation.on_morphism(automorphism)
    )
    image = bimodules.forgetful().on_morphism(bimodule_map)(group.point(epsilon))

    assert recovered is automorphism
    assert ask(image == group.point(element(0, 2))) is True
    assert ask(image == group.point(epsilon)) is False
    assert ask(field_group.point(field_element(2)) == field_group.zero()) is False


def test_matrix_base_keeps_both_actions_and_the_noncentral_diagonal() -> None:
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
    projection = relative_tensor(
        pair_bimodule.right_action(), pair_bimodule.left_action()
    )

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
    diagonal = abelian_homomorphism(
        ring_group,
        pair_group,
        lambda value: pair_element(value, value),
    )
    unit = bimodules.homomorphism(structure.unit(), pair_bimodule, diagonal)
    neutral = Monoids(structure)(multiplication, unit)
    algebras = Algebras(ring, structure)
    algebra = algebras.from_monoid(neutral)

    assert algebras.base() is ring
    assert algebras.monoid_presentation().on_object(algebra) is neutral
    assert algebras.monoid_presentation().inverse().on_object(neutral) is algebra
    assert neutral.operation() in Mor(bimodules)(tensor_square, pair_bimodule)
    assert neutral.unit_morphism() in Mor(bimodules)(structure.unit(), pair_bimodule)

    e12 = element([0, 1, 0, 0])
    e21 = element([0, 0, 1, 0])
    e11 = element([1, 0, 0, 0])
    e22 = element([0, 0, 0, 1])
    value = pair_element(e21, e21)
    left_image = pair_bimodule.left_action()(
        simple_tensor(ring_group, pair_group, e12, value)
    )
    right_image = pair_bimodule.right_action()(
        simple_tensor(pair_group, ring_group, value, e12)
    )
    assert ask(left_image == pair_group.point(pair_element(e11, e11))) is True
    assert ask(right_image == pair_group.point(pair_element(e22, e22))) is True
    assert ask(left_image == right_image) is False

    diagonal_e12 = pair_element(e12, e12)
    diagonal_e21 = pair_element(e21, e21)
    forward = componentwise_product(diagonal_e12, diagonal_e21)
    reverse = componentwise_product(diagonal_e21, diagonal_e12)
    assert (
        ask(pair_group.point(forward) == pair_group.point(pair_element(e11, e11)))
        is True
    )
    assert (
        ask(pair_group.point(reverse) == pair_group.point(pair_element(e22, e22)))
        is True
    )
    assert ask(pair_group.point(forward) == pair_group.point(reverse)) is False

    product = bimodules.forgetful().on_morphism(multiplication)
    balanced_product = product(
        balanced_tensor(
            projection,
            pair_element(e12, e21),
            pair_element(e21, e12),
        )
    )
    assert ask(balanced_product == pair_group.point(pair_element(e11, e22))) is True


test_dual_numbers_are_recovered_through_the_relative_algebra_presentation()
test_matrix_base_keeps_both_actions_and_the_noncentral_diagonal()
