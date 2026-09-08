"""Ordinary modules: rings as monoid objects in (Ab, tensor), and two module structures on F_2 over F_2 x F_2 through the two projections."""

from sage_categories.all import Sets, SelfAction, ask
from sage_categories.algebra import AbelianGroups, AbelianTensor, abelian_homomorphism, integer_group, presented_abelian_group, simple_tensor, tensor_mediator
from sage_categories.cat.modules import Modules
from sage_categories.cat.structured_objects import Monoids


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
    # 2 * 3 = 6 = 2 in Z/4.
    assert ask(ring.operation()(simple_tensor(group, group, 2 * generator, 3 * generator)) == group.point(2 * generator)) is True

    modules = Modules(ring, SelfAction(AbelianTensor()))
    regular = modules(ring.operation())
    assert regular in modules
    assert modules.forgetful().on_object(regular) is group


def test_two_projection_actions_of_the_product_ring_on_the_field() -> None:
    pairs, two = AdditiveAbelianGroup([2, 2]), AdditiveAbelianGroup([2])
    product_ring_group, product_ring = ring_in_ab(pairs, lambda a, b: pairs.linear_combination_of_smith_form_gens(vector(ZZ, [int(x) * int(y) for x, y in zip(a.vector(), b.vector())])))
    field = presented_abelian_group(two)
    modules = Modules(product_ring, SelfAction(AbelianTensor()))
    by_first = modules(tensor_mediator(product_ring_group, field, field, lambda r, m: int(r.vector()[0]) * m))
    by_second = modules(tensor_mediator(product_ring_group, field, field, lambda r, m: int(r.vector()[1]) * m))
    assert by_first in modules and by_second in modules
    assert by_first is not by_second
    assert ask(by_first == by_second) is False
    assert modules.forgetful().on_object(by_first) is field
    assert modules.forgetful().on_object(by_second) is field

    # The idempotent (1, 0) acts as the identity through the first projection and as zero through the second.
    idempotent = pairs.linear_combination_of_smith_form_gens(vector(ZZ, [1, 0]))
    scale = lambda module, scalar, value: module.action()(simple_tensor(product_ring_group, field, scalar, value))
    assert ask(scale(by_first, idempotent, two.gen(0)) == field.point(two.gen(0))) is True
    assert ask(scale(by_second, idempotent, two.gen(0)) == field.zero()) is True
    # Scalar, vector, and result keep their distinct parents.
    assert product_ring_group.point(idempotent).parent() is product_ring_group
    first_point = by_first.point(two.gen(0))
    second_point = by_second.point(two.gen(0))
    assert first_point.parent() is by_first
    assert second_point.parent() is by_second
    assert scale(by_first, idempotent, two.gen(0)).parent() is field
    first_action, second_action = by_first.action(), by_second.action()
    argument = simple_tensor(product_ring_group, field, idempotent, two.gen(0))
    assert first_action.domain() is argument.parent()
    assert first_action.codomain() is field
    assert ask(first_point + first_point == by_first.zero()) is True
    assert ask(second_point + second_point == by_second.zero()) is True

    # The module category declares one faithful functor, to Ab, and never names Sets.  The
    # composite that carries its objects to sets is built from that declaration and the one
    # Ab makes for itself.
    assert modules.forgetful().codomain() is AbelianGroups()
    assert ask(modules.is_concrete()) is True
    assert modules.functor_to_sets().codomain() is Sets
    assert modules.underlying_set(by_first) is by_first.index_set()

    # Ab is concrete, and the carrier of a module is the carrier of its underlying group.
    assert ask(AbelianGroups().is_concrete()) is True
    assert modules.underlying_set(by_first) is AbelianGroups().underlying_set(field)

    # The two actions, their existing tensor argument, and the module points retain their
    # defining owners and operations when the underlying category gains concreteness.
    assert ask(scale(by_first, idempotent, two.gen(0)) == field.point(two.gen(0))) is True
    assert ask(scale(by_second, idempotent, two.gen(0)) == field.zero()) is True
    assert by_first.action() is first_action
    assert by_second.action() is second_action
    assert first_action.domain() is argument.parent()
    assert first_action.codomain() is field
    assert ask(first_action(argument) == field.point(two.gen(0))) is True
    assert ask(second_action(argument) == field.zero()) is True
    assert first_point.parent() is by_first
    assert second_point.parent() is by_second
    assert ask(first_point + first_point == by_first.zero()) is True
    assert ask(second_point + second_point == by_second.zero()) is True
    assert first_action.base_category() is AbelianGroups()


test_residue_ring_as_monoid_object_and_its_regular_module()
test_two_projection_actions_of_the_product_ring_on_the_field()
