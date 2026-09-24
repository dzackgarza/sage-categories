"""Locally ringed spaces retain generic stalks and stalkwise-local maps."""

from sympy import true
import pytest

from sage_categories.all import Cartesian, Mor, Sets, ask
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry.locally_ringed_spaces import LocallyRingedSpaces
from sage_categories.geometry.ringed_spaces import RingedSpaces
from sage_categories.geometry.sheaves import ring_presheaf, ring_sheaf
from sage_categories.geometry.spaces import TopologicalSpaces


def residue_ring(modulus):
    carrier = Sets(tuple(range(modulus)))
    square = binary_product_data(Sets, carrier, carrier).apex()
    cartesian = Cartesian(Sets)
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % modulus)
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % modulus)
    zero = Mor(Sets)(cartesian.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(cartesian.unit(), carrier)(lambda _: 1 % modulus)
    return Rings(Sets)(addition, zero, multiplication, one)


def test_locally_ringed_owner_forgets_to_ringed_spaces_and_retains_local_stalk_maps() -> (
    None
):
    carrier = Sets((0, 1))
    empty, point_open, whole = frozenset(), frozenset((1,)), frozenset((0, 1))
    spaces = TopologicalSpaces()
    space = spaces(carrier, (empty, point_open, whole))
    field, empty_ring = residue_ring(2), residue_ring(1)
    rings = Rings(Sets)
    identity = Mor(rings)(field, field).one()
    empty_identity = Mor(rings)(empty_ring, empty_ring).one()
    to_empty = rings.homomorphism(
        field,
        empty_ring,
        Mor(Sets)(
            rings.forgetful().on_object(field),
            rings.forgetful().on_object(empty_ring),
        )(lambda _: 0),
    )
    sections = {empty: empty_ring, point_open: field, whole: field}
    identities = {empty: empty_identity, point_open: identity, whole: identity}

    def restriction(larger, smaller):
        match bool(larger), bool(smaller):
            case False, False:
                return empty_identity
            case True, False:
                return to_empty
            case True, True:
                return identity
            case False, True:
                raise AssertionError("a nonempty open is not contained in the empty open")

    restrictions = {
        (larger, smaller): restriction(larger, smaller)
        for larger in (empty, point_open, whole)
        for smaller in (empty, point_open, whole)
        if smaller <= larger
    }
    presheaf = ring_presheaf(space, sections, restrictions)

    def glue(open_key, cover, local):
        match bool(open_key):
            case False:
                return empty_ring.zero()
            case True:
                return next(
                    section
                    for member, section in zip(cover, local, strict=True)
                    if member
                )

    sheaf = ring_sheaf(presheaf, glue)
    assert ask(sheaf.glue(empty, (), ()) == empty_ring.zero()) is True
    with pytest.raises(AssertionError):
        sheaf.glue(whole, (), ())
    ringed = RingedSpaces()
    ringed_space = ringed(space, sheaf)
    locally = LocallyRingedSpaces()
    local = locally(ringed_space, lambda _point, _stalk: true)
    assert local.ringed_space() is ringed_space
    assert local.space() is space
    assert local.sheaf() is sheaf

    zero, one = carrier.point(0), carrier.point(1)
    assert local.stalk(zero) is field
    assert local.stalk(one) is field
    assert ask(local.local_ring_condition(zero)) is True
    assert ask(local.local_ring_condition(one)) is True
    assert locally.to_ringed_spaces().on_object(local) is ringed_space

    # The constant map to the open point is continuous and nonidentity.  With the
    # constant field sheaf its sheaf components and induced stalk maps are identities.
    underlying = Mor(Sets)(carrier, carrier)(lambda _: 1)
    continuous = Mor(spaces)(space, space)(underlying)
    ringed_map = ringed.homomorphism(
        ringed_space,
        ringed_space,
        continuous,
        lambda key: identities[key],
    )
    mapping = locally.homomorphism(
        local,
        local,
        ringed_map,
        lambda _point, _stalk_map: true,
    )
    assert locally.to_ringed_spaces().on_morphism(mapping) is ringed_map
    assert mapping.continuous_map() is continuous
    assert mapping.sheaf_map() is ringed_map.sheaf_map()
    assert mapping.continuous_map().underlying_map()(zero) is one
    assert mapping.stalk_map(zero).domain() is field
    assert mapping.stalk_map(zero).codomain() is field
    assert ask(mapping.stalk_map(zero) == identity) is True
    assert ask(mapping.local_map_condition(zero)) is True

    # Locality and stalk data compose here; the underlying ringed map uses the
    # generic composition already owned by RingedSpaces.
    identity_local = Mor(locally)(local, local).one()
    assert identity_local.ringed_map() is Mor(ringed)(ringed_space, ringed_space).one()
    assert ask(identity_local.stalk_map(zero) == identity) is True
    composite = mapping * mapping
    assert composite.ringed_map() is ringed_map * ringed_map
    assert composite.continuous_map().underlying_map()(zero) is one
    assert ask(composite.stalk_map(zero) == identity) is True
    assert ask(composite.local_map_condition(zero)) is True

    # A represented geometry with its own stalk evaluator can retain that evaluator
    # without routing through the finite-neighborhood stalk implementation.  Scheme
    # realizations use this boundary while remaining ordinary locally ringed spaces.
    stalk_points = []
    stalk_map_points = []

    def supplied_stalk(point):
        stalk_points.append(point)
        return field

    def supplied_stalk_map(point):
        stalk_map_points.append(point)
        return identity

    explicit = locally.with_stalks(
        ringed_space,
        supplied_stalk,
        lambda _point, _stalk: true,
    )
    assert explicit.space() is space
    assert explicit.sheaf() is sheaf
    assert explicit.stalk(zero) is field
    assert stalk_points == [zero]
    explicit_map = locally.homomorphism_with_stalks(
        explicit,
        explicit,
        ringed_map,
        supplied_stalk_map,
        lambda _point, _stalk_map: true,
    )
    assert ask(explicit_map.stalk_map(zero) == identity) is True
    assert stalk_map_points == [zero]
    assert ask(Mor(locally)(explicit, explicit).one().stalk_map(zero) == identity) is True
    assert ask((explicit_map * explicit_map).stalk_map(zero) == identity) is True


test_locally_ringed_owner_forgets_to_ringed_spaces_and_retains_local_stalk_maps()
