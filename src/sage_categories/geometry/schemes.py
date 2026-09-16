"""Schemes represented by OSCAR covered schemes and retained affine gluings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from sage_categories.algebra.commutative_rings import (
    inverse_unit,
    localization_extension,
    polynomial_ring,
    presented_ring_homomorphism,
)
from sage_categories.cat.assembly import chosen_construction
from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.leaf_categories import LeafCategory
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry._firewall import schemes as _backend
from sage_categories.geometry.affine import (
    AffineOpenCategory,
    AffineSchemesCategory,
    Spec,
    affine_structure_sheaf,
)
from sage_categories.geometry.sheaves import RingPresheaf, ring_presheaf_from_functor

__all__ = [
    "ProjectiveLinePresentation",
    "Schemes",
    "SchemesCategory",
    "TwoChartGluing",
    "native_scheme",
    "native_scheme_morphism",
    "projective_line",
]


@dataclass(frozen=True, eq=False, slots=True)
class _AffineSchemeConstruction:
    affine: AffineSchemesCategory.ObjectType


@dataclass(frozen=True, eq=False, slots=True)
class TwoChartGluing:
    left: AffineSchemesCategory.ObjectType
    right: AffineSchemesCategory.ObjectType
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_to_right_pullback: MorphismCategory.ObjectType
    right_to_left_pullback: MorphismCategory.ObjectType


@dataclass(frozen=True, eq=False, slots=True)
class ProjectiveLinePresentation:
    scheme: SchemesCategory.ObjectType
    left_chart: AffineSchemesCategory.ObjectType
    right_chart: AffineSchemesCategory.ObjectType
    left_coordinate: CategoryOfCategories.ElementType
    right_coordinate: CategoryOfCategories.ElementType
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_inclusion: SchemesCategory.MorphismType
    right_inclusion: SchemesCategory.MorphismType
    chart_swap: SchemesCategory.MorphismType
    structure_sheaf: RingPresheaf[str]
    overlap_swap: MorphismCategory.ObjectType


@dataclass(frozen=True, eq=False, slots=True)
class _ProjectiveLineCover:
    """The two affine charts, overlap localizations, and transition maps of ``P^1``."""

    left_ring: CategoryOfCategories.ElementType
    right_ring: CategoryOfCategories.ElementType
    t: CategoryOfCategories.ElementType
    u: CategoryOfCategories.ElementType
    left: AffineSchemesCategory.ObjectType
    right: AffineSchemesCategory.ObjectType
    left_root: AffineOpenCategory.ObjectType
    right_root: AffineOpenCategory.ObjectType
    left_overlap: AffineOpenCategory.ObjectType
    right_overlap: AffineOpenCategory.ObjectType
    inverse_t: CategoryOfCategories.ElementType
    right_to_left: MorphismCategory.ObjectType
    left_to_right: MorphismCategory.ObjectType


class SchemesCategory(LeafCategory):
    """Covered schemes with retained affine presentations and native mediators."""

    class ObjectType:
        def __init__(self, construction: object) -> None:
            self._construction = construction

        def construction(self) -> object:
            return self._construction

    class ElementType:
        pass

    class MorphismType:
        pass

    def _morphism_equality(
        self,
        first: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
    ) -> bool | None:
        return _backend.morphism_equal(first, second)

    def affine(self, affine: AffineSchemesCategory.ObjectType) -> SchemesCategory.ObjectType:
        """The affine scheme as a scheme, preserving its exact OSCAR chart."""
        def construct() -> SchemesCategory.ObjectType:
            construction = _AffineSchemeConstruction(affine)
            value = cast(SchemesCategory.ObjectType, self.assemble_object(construction))
            _backend.retain_affine(
                self,
                cast(CategoryOfCategories.ElementType, value),
                cast(CategoryOfCategories.ElementType, affine),
                construction,
            )
            return value

        return chosen_construction(self, "affine-scheme", (affine,), construct)

    def _covered_chart_inclusion(
        self,
        affine: AffineSchemesCategory.ObjectType,
        glued: SchemesCategory.ObjectType,
    ) -> SchemesCategory.MorphismType:
        """Reconstruct one owned chart inclusion of a retained two-chart gluing."""
        affine_scheme = self.affine(affine)
        arrow = cast(
            SchemesCategory.MorphismType,
            self.assemble_morphism(affine_scheme, glued),
        )
        _backend.retain_chart_inclusion(
            cast(MorphismCategory.ObjectType, arrow),
            cast(CategoryOfCategories.ElementType, affine),
            cast(CategoryOfCategories.ElementType, glued),
        )
        return arrow

    def glue_two_affines(
        self,
        left: AffineSchemesCategory.ObjectType,
        right: AffineSchemesCategory.ObjectType,
        left_open: AffineOpenCategory.ObjectType,
        right_open: AffineOpenCategory.ObjectType,
        left_to_right_pullback: MorphismCategory.ObjectType,
        right_to_left_pullback: MorphismCategory.ObjectType,
    ) -> tuple[
        SchemesCategory.ObjectType,
        SchemesCategory.MorphismType,
        SchemesCategory.MorphismType,
    ]:
        """Glue two affine charts along inverse principal-open maps."""
        assert left_to_right_pullback.domain() is right_open.section_ring()
        assert left_to_right_pullback.codomain() is left_open.section_ring()
        assert right_to_left_pullback.domain() is left_open.section_ring()
        assert right_to_left_pullback.codomain() is right_open.section_ring()
        construction = TwoChartGluing(
            left,
            right,
            left_open,
            right_open,
            left_to_right_pullback,
            right_to_left_pullback,
        )
        glued = cast(SchemesCategory.ObjectType, self.assemble_object(construction))
        _backend.retain_gluing(
            self,
            cast(CategoryOfCategories.ElementType, glued),
            construction,
            cast(CategoryOfCategories.ElementType, left),
            cast(CategoryOfCategories.ElementType, right),
            cast(CategoryOfCategories.ElementType, left_open),
            cast(CategoryOfCategories.ElementType, right_open),
            left_to_right_pullback,
            right_to_left_pullback,
        )
        left_inclusion = self._covered_chart_inclusion(left, glued)
        right_inclusion = self._covered_chart_inclusion(right, glued)
        return glued, left_inclusion, right_inclusion

    def gluing_mediator(
        self,
        glued: SchemesCategory.ObjectType,
        target: SchemesCategory.ObjectType,
        left_map: SchemesCategory.MorphismType,
        right_map: SchemesCategory.MorphismType,
    ) -> SchemesCategory.MorphismType:
        """The unique map induced by compatible maps on the retained two-chart presentation."""
        construction = glued.construction()
        assert isinstance(construction, TwoChartGluing)
        left_scheme, right_scheme = (
            self.affine(construction.left),
            self.affine(construction.right),
        )
        assert left_map.domain() is left_scheme and right_map.domain() is right_scheme
        assert left_map.codomain() is target and right_map.codomain() is target
        arrow = cast(
            SchemesCategory.MorphismType,
            self.assemble_morphism(glued, target),
        )
        _backend.retain_gluing_mediator(
            cast(MorphismCategory.ObjectType, arrow),
            cast(CategoryOfCategories.ElementType, glued),
            cast(CategoryOfCategories.ElementType, target),
            cast(CategoryOfCategories.ElementType, construction.left),
            cast(CategoryOfCategories.ElementType, construction.right),
            cast(MorphismCategory.ObjectType, left_map),
            cast(MorphismCategory.ObjectType, right_map),
        )
        return arrow

    def chart_map(
        self,
        source: AffineSchemesCategory.ObjectType,
        target: SchemesCategory.ObjectType,
        target_chart: AffineSchemesCategory.ObjectType,
        pullback: MorphismCategory.ObjectType,
    ) -> SchemesCategory.MorphismType:
        """A scheme map from an affine source into one retained affine chart of ``target``."""
        assert pullback.domain() is target_chart.coordinate_ring()
        assert pullback.codomain() is source.coordinate_ring()
        source_scheme = self.affine(source)
        arrow = cast(
            SchemesCategory.MorphismType,
            self.assemble_morphism(source_scheme, target),
        )
        _backend.retain_chart_map(
            cast(MorphismCategory.ObjectType, arrow),
            cast(CategoryOfCategories.ElementType, source),
            cast(CategoryOfCategories.ElementType, target),
            cast(CategoryOfCategories.ElementType, target_chart),
            pullback,
        )
        return arrow

    def __repr__(self) -> str:
        return "Schemes"


def Schemes() -> SchemesCategory:
    return cast(SchemesCategory, chosen_construction(Cat(), "schemes", (), SchemesCategory))


def native_scheme(
    value: CategoryOfCategories.ElementType,
):
    return _backend.native_scheme(value)


def native_scheme_morphism(
    value: MorphismCategory.ObjectType,
):
    return _backend.native_scheme_morphism(value)


def _projective_line_structure_sheaf(
    glued: CategoryOfCategories.ElementType,
    left_ring: CategoryOfCategories.ElementType,
    right_ring: CategoryOfCategories.ElementType,
    left_root: AffineOpenCategory.ObjectType,
    right_root: AffineOpenCategory.ObjectType,
    left_overlap: AffineOpenCategory.ObjectType,
) -> RingPresheaf[str]:
    """Retain the two-chart structure sheaf from OSCAR's sheaf on the glued scheme."""
    cover = FinitePresentedCategory(
        "ProjectiveLineAffineCover",
        ("overlap", "left", "right"),
        (("overlap->left", "overlap", "left"), ("overlap->right", "overlap", "right")),
        (),
    )
    rings = Rings(Sets).Commutative()
    overlap_ring = left_overlap.section_ring()
    left_restriction, right_restriction = _backend.structure_sheaf_restrictions(
        glued,
        left_root,
        right_root,
        left_overlap,
        left_ring,
        right_ring,
        overlap_ring,
    )

    def sections(open_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        match cover.label(cast(FinitePresentedCategory.ObjectType, open_object)):
            case "left":
                return left_ring
            case "right":
                return right_ring
            case "overlap":
                return overlap_ring
            case label:
                raise AssertionError(f"unexpected projective-line open {label!r}")

    def restriction(opposite_arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        arrow = opposite_morphism(opposite_arrow)
        path = cast(FinitePresentedCategory.MorphismType, arrow).word()
        match path:
            case ():
                section_ring = sections(arrow.domain())
                return Mor(rings)(section_ring, section_ring).one()
            case ("overlap->left",):
                return left_restriction
            case ("overlap->right",):
                return right_restriction
            case _:
                raise AssertionError(f"unexpected projective-line restriction path {path!r}")

    sheaf_functor = Fun(cover.op(), rings)(sections, restriction)

    def key_to_open(key: str) -> CategoryOfCategories.ElementType:
        return cover(key)

    def open_to_key(open_object: CategoryOfCategories.ElementType) -> str:
        return cover.label(cast(FinitePresentedCategory.ObjectType, open_object))

    return ring_presheaf_from_functor(
        glued,
        cover,
        sheaf_functor,
        key_to_open,
        open_to_key,
    )


def _projective_line_cover(field: CategoryOfCategories.ElementType) -> _ProjectiveLineCover:
    """Construct the standard affine cover of ``P^1`` and its overlap transition maps."""
    left_ring, (t,) = polynomial_ring(field, ("t",))
    right_ring, (u,) = polynomial_ring(field, ("u",))
    left = cast(AffineSchemesCategory.ObjectType, Spec.on_object(left_ring))
    right = cast(AffineSchemesCategory.ObjectType, Spec.on_object(right_ring))
    left_opens, _ = affine_structure_sheaf(left)
    right_opens, _ = affine_structure_sheaf(right)
    left_root, right_root = left_opens.root(), right_opens.root()
    left_overlap = left_opens.principal_open(left_root, t)
    right_overlap = right_opens.principal_open(right_root, u)
    left_t = left_overlap.restriction_to(left_root)(t)
    right_u = right_overlap.restriction_to(right_root)(u)
    inverse_t, inverse_u = inverse_unit(left_t), inverse_unit(right_u)
    right_to_left_base = presented_ring_homomorphism(right_ring, left_overlap.section_ring(), (inverse_t,))
    left_to_right_base = presented_ring_homomorphism(left_ring, right_overlap.section_ring(), (inverse_u,))
    return _ProjectiveLineCover(
        left_ring,
        right_ring,
        t,
        u,
        left,
        right,
        left_root,
        right_root,
        left_overlap,
        right_overlap,
        inverse_t,
        localization_extension(right_overlap.section_ring(), left_overlap.section_ring(), right_to_left_base),
        localization_extension(left_overlap.section_ring(), right_overlap.section_ring(), left_to_right_base),
    )


def _projective_line_swap(
    glued: SchemesCategory.ObjectType,
    left: AffineSchemesCategory.ObjectType,
    right: AffineSchemesCategory.ObjectType,
    left_ring: CategoryOfCategories.ElementType,
    right_ring: CategoryOfCategories.ElementType,
    t: CategoryOfCategories.ElementType,
    u: CategoryOfCategories.ElementType,
    left_overlap: AffineOpenCategory.ObjectType,
    inverse_t: CategoryOfCategories.ElementType,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    """The chart-swap automorphism of ``P^1`` and its induced overlap automorphism."""
    schemes = Schemes()
    swap_left_pullback = presented_ring_homomorphism(right_ring, left_ring, (t,))
    swap_right_pullback = presented_ring_homomorphism(left_ring, right_ring, (u,))
    left_to_glued = schemes.chart_map(left, glued, right, swap_left_pullback)
    right_to_glued = schemes.chart_map(right, glued, left, swap_right_pullback)
    swap = schemes.gluing_mediator(glued, glued, left_to_glued, right_to_glued)
    swap_overlap_base = presented_ring_homomorphism(left_ring, left_overlap.section_ring(), (inverse_t,))
    overlap_swap = localization_extension(left_overlap.section_ring(), left_overlap.section_ring(), swap_overlap_base)
    return swap, overlap_swap


def projective_line(
    field: CategoryOfCategories.ElementType,
) -> ProjectiveLinePresentation:
    """The two-chart projective line over ``field`` with its chart-swap automorphism."""
    cover = _projective_line_cover(field)
    schemes = Schemes()
    glued, left_inclusion, right_inclusion = schemes.glue_two_affines(
        cover.left,
        cover.right,
        cover.left_overlap,
        cover.right_overlap,
        cover.right_to_left,
        cover.left_to_right,
    )

    swap, overlap_swap = _projective_line_swap(
        glued,
        cover.left,
        cover.right,
        cover.left_ring,
        cover.right_ring,
        cover.t,
        cover.u,
        cover.left_overlap,
        cover.inverse_t,
    )

    structure_sheaf = _projective_line_structure_sheaf(
        glued,
        cover.left_ring,
        cover.right_ring,
        cover.left_root,
        cover.right_root,
        cover.left_overlap,
    )
    return ProjectiveLinePresentation(
        glued,
        cover.left,
        cover.right,
        cover.t,
        cover.u,
        cover.left_overlap,
        cover.right_overlap,
        left_inclusion,
        right_inclusion,
        swap,
        structure_sheaf,
        overlap_swap,
    )
