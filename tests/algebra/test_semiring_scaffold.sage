"""The Boolean semiring: both operations on one carrier, both units, and a rejected incompatible pair."""

import pytest

from sage_categories.all import Cartesian, Mor, Sets, ask
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import (
    AdditiveMonoids,
    Monoids,
    MultiplicativeMonoids,
    Semirings,
)


def boolean_operations():
    carrier = Sets((0, 1))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()
    disjunction = Mor(Sets)(square, carrier)(lambda pair: max(pair))
    conjunction = Mor(Sets)(square, carrier)(lambda pair: min(pair))
    exclusive = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % 2)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    return carrier, disjunction, conjunction, exclusive, zero, one


def test_boolean_semiring_has_two_distinct_operations() -> None:
    _, disjunction, conjunction, _, zero, one = boolean_operations()
    semirings = Semirings(Sets())
    boolean = semirings(disjunction, zero, conjunction, one)
    assert boolean in semirings

    # Both legs are retained and land in distinct named categories over the one carrier.
    additive = semirings.to_additive().on_object(boolean)
    multiplicative = semirings.to_multiplicative().on_object(boolean)
    assert additive in AdditiveMonoids(Sets()).Commutative()
    assert multiplicative in MultiplicativeMonoids(Sets())
    assert additive.addition() is disjunction
    assert multiplicative.multiplication() is conjunction

    # The semiring inherits both surfaces once: zero and + along one leg, one and * along the other.
    assert boolean.zero().parent() is boolean
    assert boolean.zero().datum() == 0
    assert boolean.one().datum() == 1
    assert (boolean.point(1) + boolean.point(1)).datum() == 1
    assert (boolean.point(1) * boolean.point(0)).datum() == 0
    assert (boolean.point(0) + boolean.point(1)).datum() == 1
    assert ask(boolean.point(1) * boolean.point(1) == boolean.one()) is True
    assert ask((boolean.point(1) + boolean.point(0)) * boolean.point(0) == boolean.zero()) is True


def test_incompatible_operations_fail_distributivity() -> None:
    _, disjunction, _, exclusive, zero, one = boolean_operations()
    # Disjunction does not distribute over exclusive disjunction: 1 ∨ (1 ⊕ 0) = 1 while (1 ∨ 1) ⊕ (1 ∨ 0) = 0.
    with pytest.raises(AssertionError):
        Semirings(Sets())(exclusive, zero, disjunction, one)


def test_semiring_morphisms_require_semiring_endpoints() -> None:
    carrier = Sets((0, 1, 2))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()
    addition = Mor(Sets)(square, carrier)(lambda pair: max(pair))
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)

    # This associative monoid distributes over max on both sides and satisfies
    # 0*x=0, but not x*0=0: its last row is constantly 2.  It therefore lies in
    # the ambient of the final semiring equifier but is not a semiring.
    multiplication = Mor(Sets)(
        square,
        carrier,
    )(
        lambda pair: (
            (0, 0, 0),
            (0, 1, 2),
            (2, 2, 2),
        )[pair[0]][pair[1]]
    )
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    additive = AdditiveMonoids(structure).renamed(Monoids(structure)(addition, zero))
    multiplicative = MultiplicativeMonoids(structure).renamed(Monoids(structure)(multiplication, one))
    semirings = Semirings(Sets())
    pairs = semirings.ambient().ambient().ambient().ambient()
    almost = semirings.ambient()(pairs((additive, multiplicative, carrier)))
    assert almost in semirings.ambient()
    assert almost not in semirings
    with pytest.raises(AssertionError):
        semirings.homomorphism(almost, almost, Mor(Sets)(carrier, carrier).one())


test_boolean_semiring_has_two_distinct_operations()
test_incompatible_operations_fail_distributivity()
test_semiring_morphisms_require_semiring_endpoints()
