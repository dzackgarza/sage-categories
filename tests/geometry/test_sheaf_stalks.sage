"""Represented sheaf stalks are retained neighborhood colimits with functorial maps."""

from sage_categories.all import Cartesian, Mor, Sets, ask
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry.ringed_spaces import RingedSpaces
from sage_categories.geometry.sheaves import ring_presheaf, ring_sheaf
from sage_categories.geometry.spaces import TopologicalSpaces
from sage_categories.geometry.stalks import (
    ring_stalk,
    ringed_stalk_map,
    stalk_diagram,
    stalk_germ,
    stalk_presentation,
)


def residue_ring(modulus):
    carrier = Sets(tuple(range(modulus)))
    square = binary_product_data(Sets, carrier, carrier).apex()
    structure = Cartesian(Sets)
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % modulus)
    multiplication = Mor(Sets)(square, carrier)(
        lambda pair: (pair[0] * pair[1]) % modulus
    )
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    return Rings(Sets)(addition, zero, multiplication, one), carrier


def residue_map(source_data, target_data, target_modulus):
    source, source_carrier = source_data
    target, target_carrier = target_data
    underlying = Mor(Sets)(source_carrier, target_carrier)(
        lambda value: value % target_modulus
    )
    return Rings(Sets).homomorphism(source, target, underlying)


def test_sierpinski_stalk_retains_nonidentity_germ_and_owned_colimit() -> None:
    carrier = Sets((0, 1))
    empty, point_open, whole = frozenset(), frozenset((1,)), frozenset((0, 1))
    space = TopologicalSpaces()(carrier, (empty, point_open, whole))
    mod_four = residue_ring(4)
    mod_two = residue_ring(2)
    rings = Rings(Sets)
    reduction = residue_map(mod_four, mod_two, 2)
    identity_two = Mor(rings)(mod_two[0], mod_two[0]).one()
    identity_four = Mor(rings)(mod_four[0], mod_four[0]).one()
    sections = {
        empty: mod_two[0],
        point_open: mod_two[0],
        whole: mod_four[0],
    }
    restrictions = {
        (empty, empty): identity_two,
        (point_open, empty): identity_two,
        (point_open, point_open): identity_two,
        (whole, empty): reduction,
        (whole, point_open): reduction,
        (whole, whole): identity_four,
    }
    presheaf = ring_presheaf(space, sections, restrictions)
    sheaf = ring_sheaf(
        presheaf,
        lambda open_set, _cover, local: sections[open_set].point(local[0].datum()),
    )

    at_one = carrier.point(1)
    stalk = ring_stalk(sheaf, at_one)
    germ = stalk_germ(sheaf, at_one, whole)
    diagram = stalk_diagram(sheaf, at_one)
    presentation = stalk_presentation(sheaf, at_one)

    assert stalk is mod_two[0]
    assert presentation.apex() is stalk
    assert presentation.diagram() is diagram
    assert germ is reduction
    assert germ.domain() is mod_four[0] and germ.codomain() is stalk
    assert germ(mod_four[0].point(3)).datum() == 1

    # At 0 the least represented neighborhood is the whole space, so the stalk
    # is Z/4 rather than the Z/2 stalk at 1.
    at_zero = carrier.point(0)
    zero_stalk = ring_stalk(sheaf, at_zero)
    assert zero_stalk is mod_four[0]
    assert stalk_germ(sheaf, at_zero, whole) is identity_four
    assert zero_stalk is not stalk


def constant_sheaf(space, ring_data):
    empty, whole = frozenset(), frozenset((0,))
    ring = ring_data[0]
    identity = Mor(Rings(Sets))(ring, ring).one()
    presheaf = ring_presheaf(
        space,
        {empty: ring, whole: ring},
        {
            (empty, empty): identity,
            (whole, empty): identity,
            (whole, whole): identity,
        },
    )
    return ring_sheaf(presheaf, lambda _open, _cover, local: local[0])


def test_induced_stalk_maps_compose_from_sheaf_and_continuous_data() -> None:
    spaces = TopologicalSpaces()
    carrier = Sets((0,))
    empty, whole = frozenset(), frozenset((0,))
    space = spaces(carrier, (empty, whole))
    two, four, eight = residue_ring(2), residue_ring(4), residue_ring(8)
    sheaf_two = constant_sheaf(space, two)
    sheaf_four = constant_sheaf(space, four)
    sheaf_eight = constant_sheaf(space, eight)
    ringed = RingedSpaces()
    source = ringed(space, sheaf_two)
    middle = ringed(space, sheaf_four)
    target = ringed(space, sheaf_eight)
    continuous = Mor(spaces)(space, space)(Mor(Sets)(carrier, carrier).one())
    four_to_two = residue_map(four, two, 2)
    eight_to_four = residue_map(eight, four, 4)
    eight_to_two = residue_map(eight, two, 2)

    first = ringed.homomorphism(source, middle, continuous, lambda _key: four_to_two)
    second = ringed.homomorphism(middle, target, continuous, lambda _key: eight_to_four)
    composite = ringed.homomorphism(
        source, target, continuous, lambda _key: eight_to_two
    )
    point = carrier.point(0)
    first_stalk = ringed_stalk_map(first, point)
    second_stalk = ringed_stalk_map(second, point)
    composite_stalk = ringed_stalk_map(composite, point)

    assert first_stalk.domain() is four[0] and first_stalk.codomain() is two[0]
    assert second_stalk.domain() is eight[0] and second_stalk.codomain() is four[0]
    assert composite_stalk.domain() is eight[0] and composite_stalk.codomain() is two[0]
    assert ask(first_stalk * second_stalk == composite_stalk) is True
    assert composite_stalk(eight[0].point(7)).datum() == 1


test_sierpinski_stalk_retains_nonidentity_germ_and_owned_colimit()
test_induced_stalk_maps_compose_from_sheaf_and_continuous_data()
