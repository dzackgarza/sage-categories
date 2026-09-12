"""Schemes represented by OSCAR covered schemes and retained affine gluings."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Any, cast

from sage_categories.algebra._commutative_rings_oscar import oscar_morphism_handle
from sage_categories.algebra.commutative_rings import (
    inverse_unit,
    localization_extension,
    polynomial_ring,
    presented_ring_homomorphism,
)
from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Fun
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealization,
    NativeMorphismRealizations,
    NativeObjectRealization,
    NativeObjectRealizations,
)
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.structured_objects import Rings
from sage_categories.engines import oscar
from sage_categories.engines.julia_bridge import OscarHandle
from sage_categories.geometry.affine import (
    AffineOpenCategory,
    AffineSchemesCategory,
    Spec,
    affine_structure_sheaf,
    native_affine_scheme,
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
    structure_sheaf: RingPresheaf
    overlap_swap: MorphismCategory.ObjectType


_objects: NativeObjectRealizations[OscarHandle, object] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[OscarHandle] = NativeMorphismRealizations()


class SchemesCategory(Category[Any, Any]):
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

    def __init__(self) -> None:
        self._affine_wrappers: dict[int, tuple[AffineSchemesCategory.ObjectType, SchemesCategory.ObjectType]] = {}
        super().__init__()

    def _from_native(self, construction: object, native: OscarHandle) -> SchemesCategory.ObjectType:
        value = self.ObjectType(construction)
        _objects.retain(self, cast(CategoryOfCategories.ElementType, value), native, construction)
        return value

    def _from_native_morphism(
        self,
        source: SchemesCategory.ObjectType,
        target: SchemesCategory.ObjectType,
        native: OscarHandle,
    ) -> SchemesCategory.MorphismType:
        assert oscar.same_native(
            oscar.covered_domain(native),
            native_scheme(cast(CategoryOfCategories.ElementType, source)).native,
        )
        assert oscar.same_native(
            oscar.covered_codomain(native),
            native_scheme(cast(CategoryOfCategories.ElementType, target)).native,
        )
        arrow = cast(
            SchemesCategory.MorphismType,
            cast(Any, self).MorphismType(domain=source, codomain=target),
        )
        _morphisms.retain(
            self,
            cast(MorphismCategory.ObjectType, arrow),
            cast(CategoryOfCategories.ElementType, source),
            cast(CategoryOfCategories.ElementType, target),
            native,
        )
        return arrow

    def affine(self, affine: AffineSchemesCategory.ObjectType) -> SchemesCategory.ObjectType:
        """The affine scheme as a scheme, preserving its exact OSCAR chart."""
        key = id(affine)
        match self._affine_wrappers.get(key):
            case (retained, value) if retained is affine:
                return value
            case _:
                native = oscar.covered_scheme(native_affine_scheme(cast(CategoryOfCategories.ElementType, affine)).native)
                value = self._from_native(_AffineSchemeConstruction(affine), native)
                self._affine_wrappers[key] = (affine, value)
                return value

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
        native_left = native_affine_scheme(cast(CategoryOfCategories.ElementType, left)).native
        native_right = native_affine_scheme(cast(CategoryOfCategories.ElementType, right)).native
        native_left_to_right = oscar.affine_morphism_direct(
            left_open.native(),
            right_open.native(),
            oscar_morphism_handle(left_to_right_pullback),
        )
        native_right_to_left = oscar.affine_morphism_direct(
            right_open.native(),
            left_open.native(),
            oscar_morphism_handle(right_to_left_pullback),
        )
        native_gluing = oscar.simple_gluing(native_left, native_right, native_left_to_right, native_right_to_left)
        native_glued = oscar.glued_covered_scheme(native_left, native_right, native_gluing)
        construction = TwoChartGluing(
            left,
            right,
            left_open,
            right_open,
            left_to_right_pullback,
            right_to_left_pullback,
        )
        glued = self._from_native(construction, native_glued)
        left_scheme, right_scheme = self.affine(left), self.affine(right)
        left_inclusion = self._from_native_morphism(
            left_scheme,
            glued,
            oscar.covered_chart_inclusion(
                native_scheme(cast(CategoryOfCategories.ElementType, left_scheme)).native,
                native_left,
                native_glued,
            ),
        )
        right_inclusion = self._from_native_morphism(
            right_scheme,
            glued,
            oscar.covered_chart_inclusion(
                native_scheme(cast(CategoryOfCategories.ElementType, right_scheme)).native,
                native_right,
                native_glued,
            ),
        )
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
        native = oscar.gluing_mediator(
            native_scheme(cast(CategoryOfCategories.ElementType, glued)).native,
            native_scheme(cast(CategoryOfCategories.ElementType, target)).native,
            native_affine_scheme(cast(CategoryOfCategories.ElementType, construction.left)).native,
            native_affine_scheme(cast(CategoryOfCategories.ElementType, construction.right)).native,
            native_scheme_morphism(cast(MorphismCategory.ObjectType, left_map)).native,
            native_scheme_morphism(cast(MorphismCategory.ObjectType, right_map)).native,
        )
        return self._from_native_morphism(glued, target, native)

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
        native_affine_map = oscar.affine_morphism_direct(
            native_affine_scheme(cast(CategoryOfCategories.ElementType, source)).native,
            native_affine_scheme(cast(CategoryOfCategories.ElementType, target_chart)).native,
            oscar_morphism_handle(pullback),
        )
        native = oscar.covered_chart_map(
            native_scheme(cast(CategoryOfCategories.ElementType, source_scheme)).native,
            native_affine_scheme(cast(CategoryOfCategories.ElementType, source)).native,
            native_scheme(cast(CategoryOfCategories.ElementType, target)).native,
            native_affine_map,
        )
        return self._from_native_morphism(source_scheme, target, native)

    def __repr__(self) -> str:
        return "Schemes"


@cache
def Schemes() -> SchemesCategory:
    return SchemesCategory()


def native_scheme(
    value: CategoryOfCategories.ElementType,
) -> NativeObjectRealization[OscarHandle, object]:
    return _objects.realization(value)


def native_scheme_morphism(
    value: MorphismCategory.ObjectType,
) -> NativeMorphismRealization[OscarHandle]:
    return _morphisms.realization(value)


def projective_line(
    field: CategoryOfCategories.ElementType,
) -> ProjectiveLinePresentation:
    """The two-chart projective line over ``field`` with its chart-swap automorphism."""
    left_ring, (t,) = polynomial_ring(field, ("t",))
    right_ring, (u,) = polynomial_ring(field, ("u",))
    left, right = Spec.on_object(left_ring), Spec.on_object(right_ring)
    left_opens, _ = affine_structure_sheaf(cast(AffineSchemesCategory.ObjectType, left))
    right_opens, _ = affine_structure_sheaf(cast(AffineSchemesCategory.ObjectType, right))
    left_root, right_root = left_opens.root(), right_opens.root()
    left_overlap = left_opens.principal_open(left_root, t)
    right_overlap = right_opens.principal_open(right_root, u)
    left_t = left_overlap.restriction_to(left_root)(t)
    right_u = right_overlap.restriction_to(right_root)(u)
    inverse_t, inverse_u = inverse_unit(left_t), inverse_unit(right_u)

    right_to_left_base = presented_ring_homomorphism(right_ring, left_overlap.section_ring(), (inverse_t,))
    left_to_right_base = presented_ring_homomorphism(left_ring, right_overlap.section_ring(), (inverse_u,))
    right_to_left = localization_extension(right_overlap.section_ring(), left_overlap.section_ring(), right_to_left_base)
    left_to_right = localization_extension(left_overlap.section_ring(), right_overlap.section_ring(), left_to_right_base)

    schemes = Schemes()
    glued, left_inclusion, right_inclusion = schemes.glue_two_affines(
        cast(AffineSchemesCategory.ObjectType, left),
        cast(AffineSchemesCategory.ObjectType, right),
        left_overlap,
        right_overlap,
        right_to_left,
        left_to_right,
    )

    swap_left_pullback = presented_ring_homomorphism(right_ring, left_ring, (t,))
    swap_right_pullback = presented_ring_homomorphism(left_ring, right_ring, (u,))
    left_to_glued = schemes.chart_map(
        cast(AffineSchemesCategory.ObjectType, left),
        glued,
        cast(AffineSchemesCategory.ObjectType, right),
        swap_left_pullback,
    )
    right_to_glued = schemes.chart_map(
        cast(AffineSchemesCategory.ObjectType, right),
        glued,
        cast(AffineSchemesCategory.ObjectType, left),
        swap_right_pullback,
    )
    swap = schemes.gluing_mediator(glued, glued, left_to_glued, right_to_glued)

    cover = FinitePresentedCategory(
        "ProjectiveLineAffineCover",
        ("overlap", "left", "right"),
        (("overlap->left", "overlap", "left"), ("overlap->right", "overlap", "right")),
        (),
    )
    rings = Rings(Sets).Commutative()
    left_restriction = left_overlap.restriction_to(left_root)
    right_restriction = right_overlap.restriction_to(right_root)
    transported_right_restriction = right_to_left * right_restriction

    def sections(
        open_object: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        match cover.label(cast(FinitePresentedCategory.ObjectType, open_object)):
            case "left":
                return left_ring
            case "right":
                return right_ring
            case "overlap":
                return left_overlap.section_ring()
            case label:
                raise AssertionError(f"unexpected projective-line open {label!r}")

    def restriction(
        opposite_arrow: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        arrow = opposite_morphism(opposite_arrow)
        path = cast(FinitePresentedCategory.MorphismType, arrow).word()
        match path:
            case ():
                section_ring = sections(arrow.domain())
                return Mor(rings)(section_ring, section_ring).one()
            case ("overlap->left",):
                return left_restriction
            case ("overlap->right",):
                return transported_right_restriction
            case _:
                raise AssertionError(f"unexpected projective-line restriction path {path!r}")

    sheaf_functor = Fun(cover.op(), rings)(sections, restriction)
    structure_sheaf = ring_presheaf_from_functor(
        glued,
        cover,
        sheaf_functor,
        lambda key: cast(CategoryOfCategories.ElementType, cover(cast(str, key))),
        lambda open_object: cover.label(cast(FinitePresentedCategory.ObjectType, open_object)),
    )
    swap_overlap_base = presented_ring_homomorphism(left_ring, left_overlap.section_ring(), (inverse_t,))
    overlap_swap = localization_extension(left_overlap.section_ring(), left_overlap.section_ring(), swap_overlap_base)
    return ProjectiveLinePresentation(
        glued,
        cast(AffineSchemesCategory.ObjectType, left),
        cast(AffineSchemesCategory.ObjectType, right),
        t,
        u,
        left_overlap,
        right_overlap,
        left_inclusion,
        right_inclusion,
        swap,
        structure_sheaf,
        overlap_swap,
    )
