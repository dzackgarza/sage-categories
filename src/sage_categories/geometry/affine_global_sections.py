"""Global sections and affine comparisons for the contravariant ``Spec`` functor."""

from __future__ import annotations

from sage_categories.cat.calculus import natural_isomorphism
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_functor, opposite_morphism
from sage_categories.geometry._ring_categories import commutative_rings as _rings
from sage_categories.geometry.affine import (
    AffineSchemes,
    AffineSchemesCategory,
    Spec,
    affine_structure_sheaf,
)

__all__ = [
    "GlobalSections",
    "affine_global_sections_comparison",
    "affine_structure_sheaf_global_map",
    "global_sections",
    "global_sections_map",
    "global_sections_spec_comparison",
]


def _global_sections_object(
    scheme: AffineSchemesCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    opens, sheaf = affine_structure_sheaf(scheme)
    ring = sheaf.section_ring(opens.root())
    assert ring is scheme.coordinate_ring()
    return ring


def _global_sections_morphism(
    opposite_mapping: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    mapping = opposite_morphism(opposite_mapping)
    assert mapping in AffineSchemes().morphism_category(1)
    return affine_structure_sheaf_global_map(mapping)


GlobalSections: Functor = Fun(AffineSchemes().op(), _rings())(
    _global_sections_object,
    _global_sections_morphism,
)


def global_sections(
    scheme: AffineSchemesCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    """The global section ring of an affine scheme, read from its structure sheaf."""
    return GlobalSections.on_object(scheme)


def affine_structure_sheaf_global_map(
    mapping: AffineSchemesCategory.MorphismType,
) -> MorphismCategory.ObjectType:
    """The structure-sheaf component on the whole affine open.

    For ``f: Spec(B) -> Spec(A)``, this is the exact pullback ``A -> B`` retained
    by the affine morphism.  Thus global sections are obtained from the same sheaf
    action rather than from a second coordinate-ring map.
    """
    source_opens, source_sheaf = affine_structure_sheaf(mapping.domain())
    target_opens, target_sheaf = affine_structure_sheaf(mapping.codomain())
    source_ring = source_sheaf.section_ring(source_opens.root())
    target_ring = target_sheaf.section_ring(target_opens.root())
    pullback = mapping.pullback()
    assert pullback.domain() is target_ring and pullback.codomain() is source_ring
    return pullback


def global_sections_map(
    mapping: AffineSchemesCategory.MorphismType,
) -> MorphismCategory.ObjectType:
    """``Gamma(f): Gamma(Y) -> Gamma(X)`` for ``f: X -> Y``."""
    return GlobalSections.on_morphism(opposite_morphism(mapping))


_RING_ROUNDTRIP = GlobalSections * opposite_functor(Spec)


def _ring_comparison_component(ring):
    result = _RING_ROUNDTRIP.on_object(ring)
    assert result is ring
    return Mor(_rings())(ring, ring).one()


global_sections_spec_comparison: NaturalTransformation = natural_isomorphism(
    _RING_ROUNDTRIP,
    Fun(_rings(), _rings()).one(),
    _ring_comparison_component,
    _ring_comparison_component,
)


_AFFINE_ROUNDTRIP = Spec * opposite_functor(GlobalSections)


def _affine_comparison_component(
    scheme: AffineSchemesCategory.ObjectType,
) -> AffineSchemesCategory.MorphismType:
    source = _AFFINE_ROUNDTRIP.on_object(scheme)
    identity = Mor(_rings())(
        scheme.coordinate_ring(),
        scheme.coordinate_ring(),
    ).one()
    return AffineSchemes().construct_morphism(source, scheme, identity)


def _affine_comparison_inverse(
    scheme: AffineSchemesCategory.ObjectType,
) -> AffineSchemesCategory.MorphismType:
    target = _AFFINE_ROUNDTRIP.on_object(scheme)
    identity = Mor(_rings())(
        scheme.coordinate_ring(),
        scheme.coordinate_ring(),
    ).one()
    return AffineSchemes().construct_morphism(scheme, target, identity)


affine_global_sections_comparison: NaturalTransformation = natural_isomorphism(
    _AFFINE_ROUNDTRIP,
    Fun(AffineSchemes(), AffineSchemes()).one(),
    _affine_comparison_component,
    _affine_comparison_inverse,
)
