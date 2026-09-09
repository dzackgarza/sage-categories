"""Compatible finite local sections glue uniquely through the retained sheaf operation."""

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
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
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
    sections = {open_set: datum[0] for open_set, datum in section_data.items()}
    restrictions = {}
    for larger in opens:
        for smaller in opens:
            if smaller <= larger:
                source, source_carrier = section_data[larger]
                target, target_carrier = section_data[smaller]
                restrictions[(larger, smaller)] = rings.homomorphism(
                    source,
                    target,
                    Mor(Sets)(source_carrier, target_carrier)(lambda value: value),
                )
    presheaf = ring_presheaf(space, sections, restrictions)

    def glue(open_set, cover, local_sections):
        assert open_set == whole and cover == (left, right)
        assert ask(presheaf.restriction(left, overlap)(local_sections[0]) == presheaf.restriction(right, overlap)(local_sections[1])) is True
        return sections[whole].point(local_sections[0].datum())

    sheaf = ring_sheaf(presheaf, glue)
    local_left, local_right = sections[left].point(3), sections[right].point(3)
    global_section = sheaf.glue(whole, (left, right), (local_left, local_right))
    assert global_section.parent() is sections[whole]
    assert global_section.datum() == 3
    assert ask(presheaf.restriction(whole, left)(global_section) == local_left) is True
    assert ask(presheaf.restriction(whole, right)(global_section) == local_right) is True


test_compatible_cover_sections_glue_uniquely()
