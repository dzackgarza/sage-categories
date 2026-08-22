"""The set layer owns carrier and cardinality operations."""

from sage.rings.integer import Integer

from sage_categories import Cardinals, FiniteSet, Sets


def test_finite_set_has_a_category_owned_surface() -> None:
    """A finite set exposes its carrier and cardinality as mathematical values."""
    finite_set = FiniteSet((Integer(2), Integer(3), Integer(5)))

    assert finite_set.category() == Sets()
    assert finite_set.elements() == (Integer(2), Integer(3), Integer(5))
    assert Integer(3) in finite_set
    assert Integer(7) not in finite_set

    cardinality = finite_set.cardinality()
    assert cardinality.category() == Cardinals()
    assert cardinality == 3
