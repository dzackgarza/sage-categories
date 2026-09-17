"""Affine schemes enter the ringed-space stack through their retained structure data."""

from sage_categories.algebra import (
    polynomial_ring,
    presented_ring_homomorphism,
    prime_field,
)
from sage_categories.all import ask
from sage_categories.geometry.affine import (
    AffineSchemes,
    AffineToLocallyRingedSpaces,
    Spec,
    affine_locally_ringed_map,
    affine_locally_ringed_space,
    affine_ring_sheaf,
    affine_ringed_space,
    affine_structure_sheaf,
    affine_topological_space,
)
from sage_categories.geometry.locally_ringed_spaces import LocallyRingedSpaces
from sage_categories.geometry.ringed_spaces import RingedSpaces


def test_affine_scheme_retains_topology_sheaf_stalks_and_maps() -> None:
    field = prime_field(5)
    source_ring, (s,) = polynomial_ring(field, ("s",))
    target_ring, (t,) = polynomial_ring(field, ("t",))
    pullback = presented_ring_homomorphism(target_ring, source_ring, (s * s,))
    source = Spec.on_object(source_ring)
    target = Spec.on_object(target_ring)
    affine_map = Spec.on_morphism(pullback.op())

    source_space = affine_topological_space(source)
    target_space = affine_topological_space(target)
    source_ringed = affine_ringed_space(source)
    target_ringed = affine_ringed_space(target)
    source_lrs = affine_locally_ringed_space(source)
    target_lrs = affine_locally_ringed_space(target)
    mapping = affine_locally_ringed_map(affine_map)

    assert source_ringed.space() is source_space
    assert target_ringed.space() is target_space
    assert source_ringed.sheaf() is affine_ring_sheaf(source)
    assert source_ringed.sheaf().presheaf.space is source_space
    assert source_lrs.ringed_space() is source_ringed
    assert target_lrs.ringed_space() is target_ringed
    assert LocallyRingedSpaces().to_ringed_spaces().on_object(source_lrs) is source_ringed
    assert RingedSpaces().to_spaces().on_object(source_ringed) is source_space

    assert AffineToLocallyRingedSpaces.on_object(source) is source_lrs
    assert AffineToLocallyRingedSpaces.on_object(target) is target_lrs
    assert AffineToLocallyRingedSpaces.on_morphism(affine_map) is mapping
    assert mapping.domain() is source_lrs and mapping.codomain() is target_lrs
    assert mapping.ringed_map().domain() is source_ringed
    assert mapping.ringed_map().codomain() is target_ringed

    source_point = AffineSchemes().spectrum_point(source, (s,))
    represented_source = source_space.carrier().point(source_point)
    assert source_lrs.stalk(represented_source) is source_point.local_ring
    assert ask(source_lrs.local_ring_condition(represented_source)) is True
    represented_target = mapping.continuous_map().underlying_map()(represented_source)
    target_point = represented_target.datum()
    assert target_point.scheme is target
    stalk_map = mapping.stalk_map(represented_source)
    assert stalk_map.codomain() is source_point.local_ring
    assert stalk_map.domain() is target_point.local_ring
    assert ask(mapping.local_map_condition(represented_source)) is True

    source_opens, _ = affine_structure_sheaf(source)
    target_opens, _ = affine_structure_sheaf(target)
    source_root = source_opens.root()
    target_root = target_opens.root()
    assert mapping.sheaf_map().component(target_root) is pullback
    target_principal = target_opens.principal_open(target_root, t)
    source_principal = mapping.continuous_map().inverse_image().on_object(target_principal)
    principal_pullback = mapping.sheaf_map().component(target_principal)
    assert principal_pullback.domain() is target_principal.section_ring()
    assert principal_pullback.codomain() is source_principal.section_ring()
    assert source_principal.parent_open() is source_root


test_affine_scheme_retains_topology_sheaf_stalks_and_maps()
