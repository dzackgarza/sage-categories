"""The Boolean semiring: both operations on one carrier, both units, and a rejected incompatible pair."""

import pytest

from sage_categories.all import Mor, Sets, Cartesian, ask
from sage_categories.cat.structured_objects import AdditiveMonoids, MultiplicativeMonoids, Semirings
from sage_categories.cat.calculus import binary_product_data


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
    carrier, disjunction, conjunction, _, zero, one = boolean_operations()
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


test_boolean_semiring_has_two_distinct_operations()
test_incompatible_operations_fail_distributivity()
