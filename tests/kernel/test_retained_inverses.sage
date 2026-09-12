"""Retained inverses persist through owned composition without symbolic replacement."""

from sage_categories.cat.morphisms import Mor
from sage_categories.sets.finite import Sets


def test_retained_inverses_compose_in_reverse_order() -> None:
    first, middle, target = Sets((0, 1)), Sets((10, 11)), Sets((20, 21))
    forward = Mor(Sets)(first, middle)({0: 10, 1: 11})
    backward = Mor(Sets)(middle, first)({10: 0, 11: 1})
    onward = Mor(Sets)(middle, target)({10: 20, 11: 21})
    returnward = Mor(Sets)(target, middle)({20: 10, 21: 11})

    Sets.retain_inverses(forward, backward)
    Sets.retain_inverses(onward, returnward)
    composite = onward * forward
    inverse = Sets.retained_inverse(composite)

    assert Sets.retained_inverse(forward) is backward
    assert Sets.retained_inverse(backward) is forward
    assert inverse is not None
    assert Sets.retained_inverse(inverse) is composite
    assert composite.inverse() is inverse
    assert inverse.inverse() is composite
    assert composite(first.point(0)) is target.point(20)
    assert composite(first.point(1)) is target.point(21)
    assert inverse(target.point(20)) is first.point(0)
    assert inverse(target.point(21)) is first.point(1)
    first_roundtrip = inverse * composite
    target_roundtrip = composite * inverse
    assert first_roundtrip(first.point(0)) is first.point(0)
    assert first_roundtrip(first.point(1)) is first.point(1)
    assert target_roundtrip(target.point(20)) is target.point(20)
    assert target_roundtrip(target.point(21)) is target.point(21)


test_retained_inverses_compose_in_reverse_order()
