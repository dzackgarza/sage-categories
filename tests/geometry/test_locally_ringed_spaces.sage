"""Locally ringed spaces retain generic stalks and stalkwise-local maps."""

from sympy import true

from sage_categories.all import Cartesian, Mor, Sets, ask
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry.locally_ringed_spaces import LocallyRingedSpaces
from sage_categories.geometry.ringed_spaces import RingedSpaces
from sage_categories.geometry.sheaves import ring_presheaf, ring_sheaf
from sage_categories.geometry.spaces import TopologicalSpaces


def field_two():
    carrier = Sets((0, 1))
    square = binary_product_data(Sets, carrier, carrier).apex()
    cartesian = Cartesian(Sets)
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % 2)
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % 2)
    zero = Mor(Sets)(cartesian.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(cartesian.unit(), carrier)(lambda _: 1)
    return Rings(Sets)(addition, zero, multiplication, one)


def test_locally_ringed_owner_forgets_to_ringed_spaces_and_retains_local_stalk_maps() -> (
    None
):
    carrier = Sets((0, 1))
    empty, point_open, whole = frozenset(), frozenset((1,)), frozenset((0, 1))
    spaces = TopologicalSpaces()
    space = spaces(carrier, (empty, point_open, whole))
    field = field_two()
    rings = Rings(Sets)
    identity = Mor(rings)(field, field).one()
    sections = {empty: field, point_open: field, whole: field}
    restrictions = {
        (larger, smaller): identity
        for larger in (empty, point_open, whole)
        for smaller in (empty, point_open, whole)
        if smaller <= larger
    }
    presheaf = ring_presheaf(space, sections, restrictions)
    sheaf = ring_sheaf(presheaf, lambda _open, _cover, local: local[0])
    ringed = RingedSpaces()
    ringed_space = ringed(space, sheaf)
    locally = LocallyRingedSpaces()
    local = locally(ringed_space, lambda _point, _stalk: true)

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
        lambda _key: identity,
    )
    mapping = locally.homomorphism(
        local,
        local,
        ringed_map,
        lambda _point, _stalk_map: true,
    )
    assert locally.to_ringed_spaces().on_morphism(mapping) is ringed_map
    assert mapping.continuous_map() is continuous
    assert mapping.continuous_map().underlying_map()(zero) is one
    assert mapping.stalk_map(zero).domain() is field
    assert mapping.stalk_map(zero).codomain() is field
    assert ask(mapping.stalk_map(zero) == identity) is True
    assert ask(mapping.local_map_condition(zero)) is True

    # Identity and composition are owned here but assembled from the retained
    # ringed-space/sheaf data.  Locality composes stalkwise.
    identity_local = Mor(locally)(local, local).one()
    assert ask(identity_local.stalk_map(zero) == identity) is True
    composite = mapping * mapping
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
