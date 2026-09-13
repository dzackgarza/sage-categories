"""Ringed-space morphisms retain their continuous map and natural sheaf action."""

from sage_categories import omega
from sage_categories.all import NN, Cartesian, Fun, Mor, Sets
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry import (
    RingedSpaces,
    TopologicalSpaces,
    ring_presheaf,
    ring_sheaf,
)
from sage_categories.geometry.sheaves import ring_presheaf_from_functor


def residue_ring(modulus):
    carrier = Sets(tuple(range(modulus)))
    square = binary_product_data(Sets, carrier, carrier).apex()
    structure = Cartesian(Sets)
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % modulus)
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % modulus)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    return Rings(Sets)(addition, zero, multiplication, one), carrier


def constant_ring_sheaf(space, ring_data):
    opens = tuple(point.datum() for point in space.opens().carrier())
    ring, _ = ring_data
    rings = Rings(Sets)
    sections = {open_set: ring for open_set in opens}
    identity = rings.morphism_category(1)(ring, ring).one()
    restrictions = {
        (larger, smaller): identity
        for larger in opens
        for smaller in opens
        if smaller <= larger
    }
    presheaf = ring_presheaf(space, sections, restrictions)
    return ring_sheaf(presheaf, lambda open_set, cover, local: sections[open_set].point(local[0].datum()))


def test_ringed_map_has_natural_sheaf_action_with_exact_endpoints() -> None:
    spaces = TopologicalSpaces()
    one = Sets((0,))
    source_space = spaces(one, (frozenset(), frozenset((0,))))
    two = Sets((0, 1))
    target_space = spaces(two, (frozenset(), frozenset((1,)), frozenset((0, 1))))
    ring_data = residue_ring(5)
    source_sheaf = constant_ring_sheaf(source_space, ring_data)
    target_sheaf = constant_ring_sheaf(target_space, ring_data)
    ringed = RingedSpaces()
    source, target = ringed(source_space, source_sheaf), ringed(target_space, target_sheaf)
    continuous = Mor(spaces)(source_space, target_space)(Mor(Sets)(one, two)(lambda _: 1))

    def component(target_open):
        source_open = continuous.inverse_image().on_object(target_space.open_object(target_open)).point().datum()
        source_ring = target_sheaf.presheaf.section_ring(target_open)
        target_ring = source_sheaf.presheaf.section_ring(source_open)
        assert source_ring is target_ring
        return Rings(Sets).morphism_category(1)(source_ring, target_ring).one()

    morphism = ringed.homomorphism(source, target, continuous, component)
    assert morphism.domain() is source and morphism.codomain() is target
    assert morphism.continuous_map() is continuous
    full = target_space.open_object(frozenset((0, 1)))
    sheaf_component = morphism.sheaf_map().component(full)
    assert sheaf_component.domain() is target_sheaf.presheaf.section_ring(frozenset((0, 1)))
    assert sheaf_component.codomain() is source_sheaf.presheaf.section_ring(frozenset((0,)))


def test_ringed_map_does_not_enumerate_a_represented_open_category() -> None:
    spaces = TopologicalSpaces()

    def represented_open_point(key):
        assert key[0] == "stage"
        return NN.point(key[1])

    def represented_open_object(key):
        assert key[0] == "stage"
        return omega(represented_open_point(key))

    space = spaces.from_open_category(
        NN,
        NN,
        omega,
        represented_open_point,
        represented_open_object,
    )
    ring, _ = residue_ring(5)
    rings = Rings(Sets).Commutative()
    assert ring in rings
    presheaf = ring_presheaf_from_functor(
        space,
        omega,
        Fun(omega.op(), rings).constant(ring),
        represented_open_object,
        lambda open_object: ("stage", open_object.point().datum()),
    )
    sheaf = ring_sheaf(presheaf, lambda _open, _cover, local: local[0])
    ringed = RingedSpaces()
    ringed_space = ringed(space, sheaf)
    continuous = spaces.morphism_with_inverse_image(
        space,
        space,
        Mor(Sets)(NN, NN).one(),
        Fun(omega, omega).one(),
    )

    def represented_component(key):
        assert key[0] == "stage"
        return Mor(rings)(ring, ring).one()

    morphism = ringed.homomorphism(
        ringed_space,
        ringed_space,
        continuous,
        represented_component,
    )
    assert morphism.domain() is ringed_space and morphism.codomain() is ringed_space
    assert morphism.continuous_map() is continuous
    assert morphism.sheaf_map().component(omega(NN.point(37))).domain() is ring


test_ringed_map_has_natural_sheaf_action_with_exact_endpoints()
test_ringed_map_does_not_enumerate_a_represented_open_category()
