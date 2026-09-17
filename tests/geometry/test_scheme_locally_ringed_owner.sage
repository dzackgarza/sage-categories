"""Schemes are same-value locally ringed spaces with retained affine covers."""

from sage_categories.algebra import (
    polynomial_ring,
    presented_ring_homomorphism,
    prime_field,
)
from sage_categories.geometry.affine import (
    Spec,
    affine_locally_ringed_map,
    affine_locally_ringed_space,
)
from sage_categories.geometry.locally_ringed_spaces import LocallyRingedSpaces
from sage_categories.geometry.ringed_spaces import RingedSpaces
from sage_categories.geometry.schemes import (
    AffineToSchemes,
    Schemes,
    native_scheme,
    native_scheme_morphism,
)
from sage_categories.geometry.spaces import TopologicalSpaces


def test_affine_scheme_is_the_same_locally_ringed_space() -> None:
    field = prime_field(5)
    source_ring, (s,) = polynomial_ring(field, ("s",))
    target_ring, (_t,) = polynomial_ring(field, ("t",))
    pullback = presented_ring_homomorphism(target_ring, source_ring, (s * s,))
    source_affine = Spec.on_object(source_ring)
    target_affine = Spec.on_object(target_ring)
    affine_map = Spec.on_morphism(pullback.op())

    schemes = Schemes()
    source = schemes.affine(source_affine)
    target = schemes.affine(target_affine)
    mapping = schemes.affine_morphism(affine_map)

    assert source is affine_locally_ringed_space(source_affine)
    assert target is affine_locally_ringed_space(target_affine)
    assert mapping is affine_locally_ringed_map(affine_map)
    assert source in schemes and target in schemes

    cover = source.affine_cover()
    assert source.local_affineness() is cover
    assert len(cover) == 1
    assert cover[0].affine is source_affine
    assert cover[0].open_immersion.domain() is source
    assert cover[0].open_immersion.codomain() is source

    to_lrs = schemes.to_locally_ringed_spaces()
    to_ringed = schemes.to_ringed_spaces()
    to_spaces = schemes.to_topological_spaces()
    assert to_lrs.domain() is schemes and to_lrs.codomain() is LocallyRingedSpaces()
    assert to_ringed.domain() is schemes and to_ringed.codomain() is RingedSpaces()
    assert to_spaces.domain() is schemes and to_spaces.codomain() is TopologicalSpaces()
    assert to_lrs.on_object(source) is source
    assert to_ringed.on_object(source) is source.ringed_space()
    assert to_spaces.on_object(source) is source.space()
    assert to_lrs.on_morphism(mapping) is mapping
    assert to_ringed.on_morphism(mapping) is mapping.ringed_map()
    assert to_spaces.on_morphism(mapping) is mapping.continuous_map()

    assert AffineToSchemes.on_object(source_affine) is source
    assert AffineToSchemes.on_object(target_affine) is target
    assert AffineToSchemes.on_morphism(affine_map) is mapping

    native_source = native_scheme(source)
    assert native_source.construction.affine is source_affine
    native_mapping = native_scheme_morphism(mapping)
    assert native_mapping.value is mapping
    assert native_mapping.source is source
    assert native_mapping.target is target


test_affine_scheme_is_the_same_locally_ringed_space()
