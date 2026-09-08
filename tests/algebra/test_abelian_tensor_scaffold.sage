"""Tensor products of presented abelian groups through their bilinear presentations and universal mediators."""

from sage_categories.all import Mor, ask
from sage_categories.algebra import (
    AbelianGroups,
    AbelianTensor,
    abelian_homomorphism,
    integer_group,
    presented_abelian_group,
    simple_tensor,
    tensor_mediator,
)
from sage_categories.cat.monoidal import MonoidalStructures, tensor_morphism, tensor_object


def test_tensor_of_cyclic_groups() -> None:
    engines = {n: AdditiveAbelianGroup([n]) for n in (2, 4, 6)}
    groups = {n: presented_abelian_group(engine) for n, engine in engines.items()}
    assert all(group in AbelianGroups() for group in groups.values())
    structure = AbelianTensor()
    assert structure in MonoidalStructures(AbelianGroups())
    tensor = structure.tensor()

    product = tensor_object(tensor, groups[4], groups[6])
    assert product in AbelianGroups()
    e4, e6, e2 = (engines[n].gen(0) for n in (4, 6, 2))

    # The simple tensor 1 (x) 1 generates, 2 (x) 3 vanishes, and 1 (x) 3 is the generator again.
    generator = simple_tensor(groups[4], groups[6], e4, e6)
    assert generator.parent() is product
    assert ask(generator == product.zero()) is False
    assert ask(simple_tensor(groups[4], groups[6], 2 * e4, 3 * e6) == product.zero()) is True
    assert ask(simple_tensor(groups[4], groups[6], e4, 3 * e6) == generator) is True

    # The biadditive map (a, b) -> ab mod 2 factors through the mediator.
    mediator = tensor_mediator(groups[4], groups[6], groups[2], lambda a, b: int(a.vector()[0]) * int(b.vector()[0]) * e2)
    assert mediator in Mor(AbelianGroups())(product, groups[2])
    assert ask(mediator(generator) == groups[2].point(e2)) is True
    assert ask(mediator(product.zero()) == groups[2].zero()) is True

    # That mediator and the map carrying e2 back to the generator are mutually inverse,
    # so the tensor is Z/2 and not merely mapped onto it.
    section = abelian_homomorphism(groups[2], product, lambda c: int(c.vector()[0]) * generator.datum())
    assert ask(mediator * section == Mor(AbelianGroups())(groups[2], groups[2]).one()) is True
    assert ask(section * mediator == Mor(AbelianGroups())(product, product).one()) is True

    # Tensoring the doubling of Z/4 with the identity of Z/6 kills the generator.
    doubling = abelian_homomorphism(groups[4], groups[4], lambda a: 2 * a)
    doubled = tensor_morphism(tensor, doubling, Mor(AbelianGroups())(groups[6], groups[6]).one())
    assert ask(doubled(generator) == product.zero()) is True
    # Tripling on the right fixes the generator: 1 (x) 3 = 3 (1 (x) 1) = 1 (x) 1 in Z/2.
    tripling = abelian_homomorphism(groups[6], groups[6], lambda b: 3 * b)
    fixed = tensor_morphism(tensor, Mor(AbelianGroups())(groups[4], groups[4]).one(), tripling)
    assert ask(fixed(generator) == generator) is True


def test_unit_comparison_acts_by_scalar_multiplication() -> None:
    six = AdditiveAbelianGroup([6])
    Z6, Z = presented_abelian_group(six), integer_group()
    structure = AbelianTensor()

    five = simple_tensor(Z, Z6, 5, six.gen(0))
    unitor = structure.left_unitor().component(Z6)
    assert ask(unitor(five) == Z6.point(5 * six.gen(0))) is True
    backward = structure.left_unitor().inverse().component(Z6)
    assert ask(backward(Z6.point(5 * six.gen(0))) == five) is True

    right = structure.right_unitor().component(Z6)
    assert ask(right(simple_tensor(Z6, Z, six.gen(0), 4)) == Z6.point(4 * six.gen(0))) is True


def test_tensor_of_integers_is_the_integers() -> None:
    integers = integer_group()
    structure = AbelianTensor()
    tensor = structure.tensor()
    product = tensor_object(tensor, integers, integers)
    one_tensor_one = simple_tensor(integers, integers, 1, 1)

    multiplication = tensor_mediator(integers, integers, integers, lambda left, right: left * right)
    section = abelian_homomorphism(integers, product, lambda value: value * one_tensor_one.datum())
    assert ask(multiplication * section == Mor(AbelianGroups())(integers, integers).one()) is True
    assert ask(section * multiplication == Mor(AbelianGroups())(product, product).one()) is True

    triples = structure.associator().domain().domain()
    associator = structure.associator().component(triples((integers, integers, integers)))
    left = simple_tensor(
        product,
        integers,
        simple_tensor(integers, integers, 2, 3).datum(),
        5,
    )
    right = simple_tensor(
        integers,
        product,
        2,
        simple_tensor(integers, integers, 3, 5).datum(),
    )
    assert ask(associator(left) == right) is True


def test_tensor_keeps_free_and_torsion_summands() -> None:
    free = FreeModule(ZZ, 2)
    mixed_engine = free / free.span([2 * free.gen(0)])
    mixed = presented_abelian_group(mixed_engine)
    mixed_orders = tuple(int(order) for order in mixed_engine.invariants())
    mixed_basis = mixed_engine.smith_form_gens()
    torsion_position = mixed_orders.index(2)
    free_position = mixed_orders.index(0)
    torsion = mixed_basis[torsion_position]
    free_value = mixed_basis[free_position]

    model_free = FreeModule(ZZ, 4)
    model_engine = model_free / model_free.span([2 * model_free.gen(index) for index in range(3)])
    model = presented_abelian_group(model_engine)
    model_orders = tuple(int(order) for order in model_engine.invariants())
    model_positions = (
        *(index for index, order in enumerate(model_orders) if order == 2),
        model_orders.index(0),
    )

    product = tensor_object(AbelianTensor().tensor(), mixed, mixed)
    tensor_basis = (
        simple_tensor(mixed, mixed, torsion, torsion).datum(),
        simple_tensor(mixed, mixed, free_value, torsion).datum(),
        simple_tensor(mixed, mixed, torsion, free_value).datum(),
        simple_tensor(mixed, mixed, free_value, free_value).datum(),
    )

    def into_model(left, right):
        left_coordinates = tuple(int(entry) for entry in left.vector())
        right_coordinates = tuple(int(entry) for entry in right.vector())
        coefficients = (
            left_coordinates[torsion_position] * right_coordinates[torsion_position],
            left_coordinates[free_position] * right_coordinates[torsion_position],
            left_coordinates[torsion_position] * right_coordinates[free_position],
            left_coordinates[free_position] * right_coordinates[free_position],
        )
        coordinates = [0] * len(model_orders)
        for position, coefficient in zip(model_positions, coefficients, strict=True):
            coordinates[position] = coefficient
        return model_engine.linear_combination_of_smith_form_gens(vector(ZZ, coordinates))

    forward = tensor_mediator(mixed, mixed, model, into_model)

    def back_to_tensor(value):
        total = 0 * tensor_basis[0]
        for position, basis_value in zip(model_positions, tensor_basis, strict=True):
            total += int(value.vector()[position]) * basis_value
        return total

    backward = abelian_homomorphism(model, product, back_to_tensor)
    assert ask(forward * backward == Mor(AbelianGroups())(model, model).one()) is True
    assert ask(backward * forward == Mor(AbelianGroups())(product, product).one()) is True


test_tensor_of_cyclic_groups()
test_unit_comparison_acts_by_scalar_multiplication()
test_tensor_of_integers_is_the_integers()
test_tensor_keeps_free_and_torsion_summands()
