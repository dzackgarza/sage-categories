"""Compatible finite local sections glue uniquely through the retained sheaf operation."""

import pytest

from sage_categories.all import Mor, Sets, Cartesian, ask
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry import TopologicalSpaces, ring_presheaf, ring_sheaf


def residue_ring(modulus):
    carrier = Sets(tuple(range(modulus)))
    square = binary_product_data(Sets, carrier, carrier).apex()
    structure = Cartesian(Sets)
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % modulus)
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % modulus)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1 % modulus)
    return Rings(Sets)(addition, zero, multiplication, one), carrier


def test_compatible_cover_sections_glue_uniquely() -> None:
    carrier = Sets((0, 1, 2))
    empty = frozenset()
    left = frozenset((0, 2))
    right = frozenset((1, 2))
    overlap = frozenset((2,))
    whole = frozenset((0, 1, 2))
    space = TopologicalSpaces()(carrier, (empty, overlap, left, right, whole))
    rings = Rings(Sets)
    opens = (empty, overlap, left, right, whole)
    section_data = {open_set: residue_ring(5) for open_set in opens}
    section_data[empty] = residue_ring(1)
    sections = {open_set: datum[0] for open_set, datum in section_data.items()}

    def restriction_rule(smaller):
        match bool(smaller):
            case False:
                return lambda _: 0
            case True:
                return lambda value: value

    restrictions = {}
    for larger in opens:
        for smaller in opens:
            if smaller <= larger:
                source, source_carrier = section_data[larger]
                target, target_carrier = section_data[smaller]
                restrictions[(larger, smaller)] = rings.homomorphism(
                    source,
                    target,
                    Mor(Sets)(source_carrier, target_carrier)(restriction_rule(smaller)),
                )
    presheaf = ring_presheaf(space, sections, restrictions)

    def glue(open_set, cover, local_sections):
        match bool(open_set):
            case False:
                return sections[empty].zero()
            case True:
                local = next(
                    section
                    for member, section in zip(cover, local_sections, strict=True)
                    if member
                )
                return sections[open_set].point(local.datum())

    sheaf = ring_sheaf(presheaf, glue)
    local_left, local_right = sections[left].point(3), sections[right].point(3)
    global_section = sheaf.glue(whole, (left, right), (local_left, local_right))
    assert global_section.parent() is sections[whole]
    assert global_section.datum() == 3
    assert ask(presheaf.restriction(whole, left)(global_section) == local_left) is True
    assert ask(presheaf.restriction(whole, right)(global_section) == local_right) is True
    assert ask(sheaf.glue(empty, (), ()) == sections[empty].zero()) is True
    with pytest.raises(AssertionError):
        sheaf.glue(whole, (), ())
    with pytest.raises(AssertionError):
        sheaf.glue(whole, (left, right), (local_left, sections[right].point(4)))

    # An empty cover has a unique matching family. Its amalgamation is unique
    # exactly when the empty-open section ring has one element.
    bad_empty_space = TopologicalSpaces()(Sets(()), (empty,))
    nonzero_ring, _ = residue_ring(5)
    bad_presheaf = ring_presheaf(
        bad_empty_space,
        {empty: nonzero_ring},
        {(empty, empty): Mor(rings)(nonzero_ring, nonzero_ring).one()},
    )
    bad_sheaf = ring_sheaf(bad_presheaf, lambda _open, _cover, _local: nonzero_ring.zero())
    with pytest.raises(AssertionError):
        bad_sheaf.glue(empty, (), ())


test_compatible_cover_sections_glue_uniquely()
