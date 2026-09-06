"""The tensor product of finite abelian groups: Z/4 (x) Z/6 = Z/2 through its bilinear presentation, the mediator, tensoring maps, and the unit comparison."""

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


test_tensor_of_cyclic_groups()
test_unit_comparison_acts_by_scalar_multiplication()
