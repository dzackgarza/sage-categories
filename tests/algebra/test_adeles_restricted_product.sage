"""The adeles retain all finite components and the restricted-product topology."""

from fractions import Fraction

from sage_categories.algebra import adeles_of_rationals


def test_adeles_retain_components_ring_operations_and_diagonal() -> None:
    adeles = adeles_of_rationals()
    assert adeles.primes.point(101).datum() == 101
    assert adeles.open_object(adeles.empty_open).category() is adeles.space.open_category()
    assert adeles.open_object(adeles.whole_open).category() is adeles.space.open_category()
    one = adeles.ring.one()
    one_value = one.datum()
    assert one_value.exceptional_primes == frozenset()
    for prime in (2, 3, 101, 1009):
        component = one_value.finite_component(prime)
        assert component.rational_value() == 1
        assert component.is_integral() is True

    rational = adeles.rational_field.value(Fraction(1, 5))
    diagonal = adeles.diagonal_map()(rational)
    diagonal_value = diagonal.datum()
    assert diagonal_value.exceptional_primes == frozenset({5})
    assert diagonal_value.finite_component(5).valuation() == -1
    assert diagonal_value.finite_component(7).valuation() == 0
    assert diagonal_value.certifies_integral_at(7)

    real_component = adeles.component_map("real")
    five_component = adeles.component_map(5)
    seven_component = adeles.component_map(7)
    assert real_component.domain() is adeles.ring
    assert real_component.codomain() is adeles.real_field.ring
    assert real_component(diagonal).datum().rational_value() == Fraction(1, 5)
    assert five_component.domain() is adeles.ring
    assert five_component.codomain() is adeles.local_field(5).ring
    assert seven_component(diagonal).datum().rational_value() == Fraction(1, 5)
    assert adeles.diagonal_map().domain() is adeles.rational_field.ring
    assert adeles.diagonal_map().codomain() is adeles.ring

    total = one + diagonal
    product = one * diagonal
    assert five_component(total).datum().rational_value() == Fraction(6, 5)
    assert five_component(product).datum().rational_value() == Fraction(1, 5)


def test_adele_basic_open_retains_finite_exceptional_data() -> None:
    adeles = adeles_of_rationals()
    basic = adeles.basic_open(
        lambda value: value.rational_value() is not None,
        {5: lambda value: value.valuation() is not None},
    )
    assert basic.exceptional_primes == frozenset({5})
    assert basic.uses_integral_condition(7)
    assert not basic.uses_integral_condition(5)
    diagonal = adeles.diagonal_value(Fraction(1, 5))
    assert basic.contains(diagonal) is True
    open_object = adeles.open_object(basic)
    addition_preimage = adeles.topological_ring.addition_preimage(open_object)
    multiplication_preimage = adeles.topological_ring.multiplication_preimage(open_object)
    zero = adeles.zero_value()
    one = adeles.one_value()
    assert addition_preimage.contains(zero, diagonal) is True
    assert multiplication_preimage.contains(one, diagonal) is True


test_adeles_retain_components_ring_operations_and_diagonal()
test_adele_basic_open_retains_finite_exceptional_data()
