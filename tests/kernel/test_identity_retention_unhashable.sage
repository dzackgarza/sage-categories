"""Identity-retained choices accept unhashable owned parameters."""

from sage_categories.all import Sets
from sage_categories.cat.choices import ChosenConstruction
from sage_categories.kernel.construction import (
    retain_object_by_datum,
    retained_object_by_datum,
)


def test_unhashable_parameters_are_retained_by_identity():
    construction = ChosenConstruction()
    owner = object()
    parameter = [1, 2, 3]
    equal_but_distinct = [1, 2, 3]
    first = object()
    second = object()

    assert construction(owner, (parameter,), lambda: first) is first
    assert construction(owner, (parameter,), lambda: object()) is first
    assert construction(owner, (equal_but_distinct,), lambda: second) is second
    assert second is not first


def test_unhashable_exact_data_canonicalize_by_equality():
    value = Sets((0,))
    datum = [4, 5, 6]
    equal_but_distinct = [4, 5, 6]

    retain_object_by_datum(Sets, datum, value)
    assert retained_object_by_datum(Sets, datum) is value
    assert retained_object_by_datum(Sets, equal_but_distinct) is value


test_unhashable_parameters_are_retained_by_identity()
test_unhashable_exact_data_canonicalize_by_equality()
