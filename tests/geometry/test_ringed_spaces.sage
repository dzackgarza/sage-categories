"""Ringed-space morphisms retain their continuous map and natural sheaf action."""

from sage_categories.all import Mor, Sets, Cartesian
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry import RingedSpaces, TopologicalSpaces, ring_presheaf, ring_sheaf


def residue_ring(modulus):
    carrier = Sets(tuple(range(modulus)))
    square = binary_product_data(Sets, carrier, carrier).apex()
    structure = Cartesian(Sets)
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % modulus)
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % modulus)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    return Rings(Sets)(addition, zero, multiplication, one), carrier


def constant_ring_sheaf(space):
    opens = tuple(point.datum() for point in space.opens().carrier())
    rings = Rings(Sets)
    section_data = {open_set: residue_ring(5) for open_set in opens}
    sections = {open_set: value[0] for open_set, value in section_data.items()}
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
    return ring_sheaf(presheaf, lambda open_set, cover, local: sections[open_set].point(local[0].datum()))


def test_ringed_map_has_natural_sheaf_action_with_exact_endpoints() -> None:
    spaces = TopologicalSpaces()
    one = Sets((0,))
    source_space = spaces(one, (frozenset(), frozenset((0,))))
    two = Sets((0, 1))
    target_space = spaces(two, (frozenset(), frozenset((1,)), frozenset((0, 1))))
    source_sheaf, target_sheaf = constant_ring_sheaf(source_space), constant_ring_sheaf(target_space)
    ringed = RingedSpaces()
    source, target = ringed(source_space, source_sheaf), ringed(target_space, target_sheaf)
    continuous = Mor(spaces)(source_space, target_space)(Mor(Sets)(one, two)(lambda _: 1))

    def component(target_open):
        source_open = continuous.inverse_image().on_object(target_space.open_object(target_open)).point().datum()
        source_ring = target_sheaf.presheaf.section_ring(target_open)
        target_ring = source_sheaf.presheaf.section_ring(source_open)
        source_carrier = Rings(Sets).forgetful().on_object(source_ring)
        target_carrier = Rings(Sets).forgetful().on_object(target_ring)
        return Rings(Sets).homomorphism(
            source_ring,
            target_ring,
            Mor(Sets)(source_carrier, target_carrier)(lambda value: value),
        )

    morphism = ringed.homomorphism(source, target, continuous, component)
    assert morphism.domain() is source and morphism.codomain() is target
    assert morphism.continuous_map() is continuous
    full = target_space.open_object(frozenset((0, 1)))
    sheaf_component = morphism.sheaf_map().component(full)
    assert sheaf_component.domain() is target_sheaf.presheaf.section_ring(frozenset((0, 1)))
    assert sheaf_component.codomain() is source_sheaf.presheaf.section_ring(frozenset((0,)))


test_ringed_map_has_natural_sheaf_action_with_exact_endpoints()
