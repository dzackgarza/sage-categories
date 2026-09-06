"""Ordinary modules: rings as monoid objects in (Ab, tensor), and two module structures on F_2 over F_2 x F_2 through the two projections."""

from sage_categories.all import Mor, SelfAction, ask
from sage_categories.algebra import AbelianGroups, AbelianTensor, abelian_homomorphism, bilinear_map, integer_group, presented_abelian_group, tensor_mediator
from sage_categories.cat.modules import Modules
from sage_categories.cat.structured_objects import Monoids
from sage_categories.cat.monoidal import tensor_object


def ring_in_ab(engine, multiply):
    """The monoid object of (Ab, tensor) on a presented group with a biadditive multiplication rule and the unit sending 1 to ``one``."""
    group = presented_abelian_group(engine)
    one = engine.linear_combination_of_smith_form_gens(vector(ZZ, [1] * len(engine.invariants())))
    multiplication = tensor_mediator(group, group, group, multiply)
    unit = abelian_homomorphism(integer_group(), group, lambda k: k * one)
    return group, Monoids(AbelianTensor())(multiplication, unit)


def test_residue_ring_as_monoid_object_and_its_regular_module() -> None:
    four = AdditiveAbelianGroup([4])
    group, ring = ring_in_ab(four, lambda a, b: int(a.vector()[0]) * b)
    assert ring in Monoids(AbelianTensor())
    generator = four.gen(0)
    assert ring.operation()(tensor_object(AbelianTensor().tensor(), group, group).point(bilinear_map(group, group)(bilinear_map(group, group).domain().point((2 * generator, 3 * generator))).datum())).datum() == 2 * generator
    regular = Modules(ring, SelfAction(AbelianTensor()))(ring.operation())
    assert regular in Modules(ring, SelfAction(AbelianTensor()))
    assert Modules(ring, SelfAction(AbelianTensor())).forgetful().on_object(regular) is group


def test_two_projection_actions_of_the_product_ring_on_the_field() -> None:
    pairs, two = AdditiveAbelianGroup([2, 2]), AdditiveAbelianGroup([2])
    product_ring_group, product_ring = ring_in_ab(pairs, lambda a, b: pairs.linear_combination_of_smith_form_gens(vector(ZZ, [int(x) * int(y) for x, y in zip(a.vector(), b.vector())])))
    field = presented_abelian_group(two)
    modules = Modules(product_ring, SelfAction(AbelianTensor()))
    acted = tensor_object(AbelianTensor().tensor(), product_ring_group, field)
    by_first = modules(tensor_mediator(product_ring_group, field, field, lambda r, m: int(r.vector()[0]) * m))
    by_second = modules(tensor_mediator(product_ring_group, field, field, lambda r, m: int(r.vector()[1]) * m))
    assert by_first in modules and by_second in modules
    assert by_first is not by_second
    assert ask(by_first == by_second) is False
    assert modules.forgetful().on_object(by_first) is field
    assert modules.forgetful().on_object(by_second) is field

    # The idempotent (1, 0) acts as the identity through the first projection and as zero through the second.
    idempotent = pairs.linear_combination_of_smith_form_gens(vector(ZZ, [1, 0]))
    scalar_times_generator = bilinear_map(product_ring_group, field)(bilinear_map(product_ring_group, field).domain().point((idempotent, two.gen(0)))).datum()
    assert by_first.action()(acted.point(scalar_times_generator)).datum() == two.gen(0)
    assert by_second.action()(acted.point(scalar_times_generator)).datum() == two.zero()
    # Scalar, vector, and result keep their distinct parents.
    assert product_ring_group.point(idempotent).parent() is product_ring_group
    assert by_first.point(two.gen(0)).parent() is by_first
    assert by_first.action()(acted.point(scalar_times_generator)).parent() is field


test_residue_ring_as_monoid_object_and_its_regular_module()
test_two_projection_actions_of_the_product_ring_on_the_field()
