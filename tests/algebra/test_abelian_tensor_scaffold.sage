"""The tensor product of finite abelian groups: Z/4 (x) Z/6 = Z/2 through its bilinear presentation, the mediator, tensoring maps, and the unit comparison."""

from sage_categories.all import Mor, ask
from sage_categories.algebra import (
    AbelianGroups,
    AbelianTensor,
    abelian_homomorphism,
    bilinear_map,
    integer_group,
    presented_abelian_group,
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
    bilinear = bilinear_map(groups[4], groups[6])
    pairs = bilinear.domain()
    generator = bilinear(pairs.point((e4, e6))).datum()
    assert generator != product.zero().datum()
    assert bilinear(pairs.point((2 * e4, 3 * e6))).datum() == product.zero().datum()
    assert bilinear(pairs.point((e4, 3 * e6))).datum() == generator

    # The biadditive map (a, b) -> ab mod 2 factors through the mediator.
    mediator = tensor_mediator(groups[4], groups[6], groups[2], lambda a, b: int(a.vector()[0]) * int(b.vector()[0]) * e2)
    assert mediator in Mor(AbelianGroups())(product, groups[2])
    assert mediator(product.point(generator)).datum() == e2
    assert mediator(product.zero()).datum() == groups[2].zero().datum()

    # That mediator and the map carrying e2 back to the generator are mutually inverse,
    # so the tensor is Z/2 and not merely mapped onto it.
    section = abelian_homomorphism(groups[2], product, lambda c: int(c.vector()[0]) * generator)
    assert ask(mediator * section == Mor(AbelianGroups())(groups[2], groups[2]).one()) is True
    assert ask(section * mediator == Mor(AbelianGroups())(product, product).one()) is True

    # Tensoring the doubling of Z/4 with the identity of Z/6 kills the generator.
    doubling = abelian_homomorphism(groups[4], groups[4], lambda a: 2 * a)
    doubled = tensor_morphism(tensor, doubling, Mor(AbelianGroups())(groups[6], groups[6]).one())
    assert doubled(product.point(generator)).datum() == product.zero().datum()
    # Tripling on the right fixes the generator: 1 (x) 3 = 3 (1 (x) 1) = 1 (x) 1 in Z/2.
    tripling = abelian_homomorphism(groups[6], groups[6], lambda b: 3 * b)
    assert tensor_morphism(tensor, Mor(AbelianGroups())(groups[4], groups[4]).one(), tripling)(product.point(generator)).datum() == generator


def test_unit_comparison_acts_by_scalar_multiplication() -> None:
    six = AdditiveAbelianGroup([6])
    Z6, Z = presented_abelian_group(six), integer_group()
    structure = AbelianTensor()
    left = tensor_object(structure.tensor(), Z, Z6)
    bilinear = bilinear_map(Z, Z6)
    five = bilinear(bilinear.domain().point((5, six.gen(0)))).datum()
    unitor = structure.left_unitor().component(Z6)
    assert unitor(left.point(five)).datum() == 5 * six.gen(0)
    backward = structure.left_unitor().inverse().component(Z6)
    assert backward(Z6.point(5 * six.gen(0))).datum() == five
    right = structure.right_unitor().component(Z6)
    assert right(tensor_object(structure.tensor(), Z6, Z).point(bilinear_map(Z6, Z)(bilinear_map(Z6, Z).domain().point((six.gen(0), 4))).datum())).datum() == 4 * six.gen(0)


test_tensor_of_cyclic_groups()
test_unit_comparison_acts_by_scalar_multiplication()
