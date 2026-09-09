"""A ring-valued presheaf retains exact restriction maps and their contravariant composition."""

from sage_categories.all import Mor, Sets, Cartesian, ask
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry import TopologicalSpaces, ring_presheaf


def residue_ring(modulus):
    carrier = Sets(tuple(range(modulus)))
    square = binary_product_data(Sets, carrier, carrier).apex()
    structure = Cartesian(Sets)
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % modulus)
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % modulus)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    return Rings(Sets)(addition, zero, multiplication, one), carrier


def test_restrictions_are_owned_ring_maps_and_compose_contravariantly() -> None:
    carrier = Sets((0, 1))
    empty, point, whole = frozenset(), frozenset((1,)), frozenset((0, 1))
    space = TopologicalSpaces()(carrier, (empty, point, whole))
    rings = Rings(Sets)
    section_data = {open_set: residue_ring(5) for open_set in (empty, point, whole)}
    sections = {open_set: datum[0] for open_set, datum in section_data.items()}

    restrictions = {}
    for larger in (empty, point, whole):
        for smaller in (empty, point, whole):
            if smaller <= larger:
                source, source_carrier = section_data[larger]
                target, target_carrier = section_data[smaller]
                underlying = Mor(Sets)(source_carrier, target_carrier)(lambda value: value)
                restrictions[(larger, smaller)] = rings.homomorphism(source, target, underlying)

    sheaf_data = ring_presheaf(space, sections, restrictions)
    whole_to_point = sheaf_data.restriction(whole, point)
    point_to_empty = sheaf_data.restriction(point, empty)
    whole_to_empty = sheaf_data.restriction(whole, empty)
    assert whole_to_point.domain() is sections[whole] and whole_to_point.codomain() is sections[point]
    assert ask(point_to_empty * whole_to_point == whole_to_empty) is True
    assert whole_to_point(sections[whole].point(3)).datum() == 3
    assert sheaf_data.functor.domain() is space.open_category().op()


test_restrictions_are_owned_ring_maps_and_compose_contravariantly()
