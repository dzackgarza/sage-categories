"""Schemes represented by OSCAR covered schemes and retained affine gluings."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from typing import Any, cast

from sympy import false, true

from sage_categories.algebra._certified_commutative_ring import (
    certified_commutative_ring,
)
from sage_categories.algebra.commutative_rings import (
    integer_ring,
    inverse_unit,
    localization_extension,
    polynomial_ring,
    presented_ring_homomorphism,
    prime_contains,
    prime_generators,
    prime_ideal_equal,
    prime_ideal_extension,
    prime_ideal_preimage,
)
from sage_categories.cat.assembly import (
    chosen_construction,
    select_value,
    selected_value,
)
from sage_categories.cat.calculus import natural_isomorphism
from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.leaf_categories import LeafCategory, ParameterizedThinCategory
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import ask, assume
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.structured_objects import Rings
from sage_categories.geometry._firewall import schemes as _backend
from sage_categories.geometry._ring_categories import commutative_rings as _rings
from sage_categories.geometry.affine import (
    AffineOpenCategory,
    AffineSchemes,
    AffineSchemesCategory,
    AffineSpectrumPoint,
    Spec,
    affine_locally_ringed_map,
    affine_locally_ringed_space,
    affine_structure_sheaf,
    affine_topological_space,
)
from sage_categories.geometry.locally_ringed_spaces import (
    LocallyRingedSpaces,
    LocallyRingedSpacesCategory,
)
from sage_categories.geometry.ringed_spaces import RingedSpaces, RingedSpacesCategory
from sage_categories.geometry.sheaves import (
    RingPresheaf,
    RingSheaf,
    ring_presheaf_from_functor,
    ring_sheaf,
)
from sage_categories.geometry.spaces import TopologicalSpaces, TopologicalSpacesCategory

__all__ = [
    "AffineOpenChart",
    "AffineOverlap",
    "AffineOverlapPiece",
    "AffineToSchemes",
    "FiniteAffineGluing",
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
class AffineOpenChart:
    """One affine member of a retained scheme cover and its open immersion."""

    affine: AffineSchemesCategory.ObjectType
    open_immersion: MorphismCategory.ObjectType
    structure_sheaf_comparison: NaturalTransformation


@dataclass(frozen=True, eq=False, slots=True)
class AffineOverlapPiece:
    """One affine piece of a represented overlap and its inverse transition maps."""

    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_to_right_pullback: MorphismCategory.ObjectType
    right_to_left_pullback: MorphismCategory.ObjectType


@dataclass(frozen=True, eq=False, slots=True)
class AffineOverlap:
    """A pairwise chart overlap represented by a finite affine cover."""

    left: int
    right: int
    pieces: tuple[AffineOverlapPiece, ...]
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType


@dataclass(frozen=True, eq=False, slots=True)
class FiniteAffineGluing:
    """Finite affine charts with complete pairwise overlap data."""

    charts: tuple[AffineSchemesCategory.ObjectType, ...]
    overlaps: tuple[AffineOverlap, ...]

    def overlap(self, first: int, second: int) -> AffineOverlap:
        left, right = sorted((first, second))
        for overlap in self.overlaps:
            match overlap.left == left and overlap.right == right:
                case True:
                    return overlap
                case False:
                    pass
        raise AssertionError(f"missing overlap for chart pair {(left, right)!r}")


@dataclass(frozen=True, eq=False, slots=True)
class _TaggedAffinePoint:
    presentation: FiniteAffineGluing
    chart: int
    point: AffineSpectrumPoint


@dataclass(frozen=True, eq=False, slots=True)
class _SchemeOpenData:
    presentation: FiniteAffineGluing
    chart: int
    affine_open: AffineOpenCategory.ObjectType
    chart_opens: tuple[AffineOpenCategory.ObjectType, ...]


class SchemeOpenCategory(ParameterizedThinCategory):
    """Chart-affine basis opens of one finite glued scheme."""

    class ObjectType:
        def __init__(self, data: _SchemeOpenData) -> None:
            self._data = data

        def presentation(self) -> FiniteAffineGluing:
            return self._data.presentation

        def chart(self) -> int:
            return self._data.chart

        def affine_open(self) -> AffineOpenCategory.ObjectType:
            return self._data.affine_open

        def chart_opens(self) -> tuple[AffineOpenCategory.ObjectType, ...]:
            return self._data.chart_opens

        def chart_open(self, index: int) -> AffineOpenCategory.ObjectType:
            return self._data.chart_opens[index]

        def section_ring(self) -> CategoryOfCategories.ElementType:
            return _compatible_sections_ring(self)

        def restriction_to(self, larger: SchemeOpenCategory.ObjectType) -> MorphismCategory.ObjectType:
            return cast(SchemeOpenCategory, self.parent()).restriction_map(self, larger)

    class ElementType:
        pass

    class MorphismType:
        pass

    def presentation(self) -> FiniteAffineGluing:
        return cast(FiniteAffineGluing, self.parameter(0))

    def open(
        self,
        chart: int,
        affine_open: AffineOpenCategory.ObjectType,
    ) -> SchemeOpenCategory.ObjectType:
        presentation = self.presentation()
        assert 0 <= chart < len(presentation.charts)
        assert affine_open.scheme() is presentation.charts[chart]

        def construct() -> CategoryOfCategories.ElementType:
            chart_opens = tuple(
                _finite_chart_preimage_affine_open(
                    presentation,
                    source_chart,
                    chart,
                    affine_open,
                )
                for source_chart in range(len(presentation.charts))
            )
            return self.assemble_object(
                _SchemeOpenData(presentation, chart, affine_open, chart_opens)
            )

        return cast(
            SchemeOpenCategory.ObjectType,
            chosen_construction(
                self,
                "chart-affine-open",
                (chart, affine_open),
                construct,
            ),
        )

    def from_chart_opens(
        self,
        chart_opens: tuple[AffineOpenCategory.ObjectType, ...],
    ) -> SchemeOpenCategory.ObjectType:
        """Retain one global open from compatible chart-local representatives."""
        presentation = self.presentation()
        assert len(chart_opens) == len(presentation.charts)
        for chart, affine_open in zip(presentation.charts, chart_opens, strict=True):
            assert affine_open.scheme() is chart
        assert _backend.finite_open_family_compatible(presentation, chart_opens)
        return cast(
            SchemeOpenCategory.ObjectType,
            chosen_construction(
                self,
                "global-open",
                chart_opens,
                lambda: self.assemble_object(
                    _SchemeOpenData(presentation, 0, chart_opens[0], chart_opens)
                ),
            ),
        )

    def restriction_map(
        self,
        smaller: SchemeOpenCategory.ObjectType,
        larger: SchemeOpenCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        match smaller is larger:
            case True:
                return Mor(_rings())(larger.section_ring(), larger.section_ring()).one()
            case False:
                return _compatible_sections_restriction(smaller, larger)

    def _admits_morphism(
        self,
        domain: SchemeOpenCategory.ObjectType,
        codomain: SchemeOpenCategory.ObjectType,
    ) -> bool:
        match domain is codomain:
            case True:
                return True
            case False:
                return all(
                    _backend.finite_open_contains(self.presentation(), smaller, larger)
                    for smaller, larger in zip(
                        domain.chart_opens(),
                        codomain.chart_opens(),
                        strict=True,
                    )
                )

    def __repr__(self) -> str:
        return f"SchemeOpens({len(self.presentation().charts)} charts)"


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
    scheme: CategoryOfCategories.ElementType
    left_chart: AffineSchemesCategory.ObjectType
    right_chart: AffineSchemesCategory.ObjectType
    left_coordinate: CategoryOfCategories.ElementType
    right_coordinate: CategoryOfCategories.ElementType
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_inclusion: MorphismCategory.ObjectType
    right_inclusion: MorphismCategory.ObjectType
    chart_swap: MorphismCategory.ObjectType
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


class _OscarCoveredSchemesCategory(LeafCategory):
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

    def affine(self, affine: AffineSchemesCategory.ObjectType) -> _OscarCoveredSchemesCategory.ObjectType:
        """The affine scheme as a scheme, preserving its exact OSCAR chart."""
        def construct() -> _OscarCoveredSchemesCategory.ObjectType:
            construction = _AffineSchemeConstruction(affine)
            value = cast(_OscarCoveredSchemesCategory.ObjectType, self.assemble_object(construction))
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
        glued: _OscarCoveredSchemesCategory.ObjectType,
    ) -> _OscarCoveredSchemesCategory.MorphismType:
        """Reconstruct one owned chart inclusion of a retained two-chart gluing."""
        affine_scheme = self.affine(affine)
        arrow = cast(
            _OscarCoveredSchemesCategory.MorphismType,
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
        _OscarCoveredSchemesCategory.ObjectType,
        _OscarCoveredSchemesCategory.MorphismType,
        _OscarCoveredSchemesCategory.MorphismType,
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
        glued = cast(_OscarCoveredSchemesCategory.ObjectType, self.assemble_object(construction))
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
        glued: _OscarCoveredSchemesCategory.ObjectType,
        target: _OscarCoveredSchemesCategory.ObjectType,
        left_map: _OscarCoveredSchemesCategory.MorphismType,
        right_map: _OscarCoveredSchemesCategory.MorphismType,
    ) -> _OscarCoveredSchemesCategory.MorphismType:
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
            _OscarCoveredSchemesCategory.MorphismType,
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
        target: _OscarCoveredSchemesCategory.ObjectType,
        target_chart: AffineSchemesCategory.ObjectType,
        pullback: MorphismCategory.ObjectType,
    ) -> _OscarCoveredSchemesCategory.MorphismType:
        """A scheme map from an affine source into one retained affine chart of ``target``."""
        assert pullback.domain() is target_chart.coordinate_ring()
        assert pullback.codomain() is source.coordinate_ring()
        source_scheme = self.affine(source)
        arrow = cast(
            _OscarCoveredSchemesCategory.MorphismType,
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
        return "OscarCoveredSchemes"


def _covered_schemes() -> _OscarCoveredSchemesCategory:
    return cast(
        _OscarCoveredSchemesCategory,
        chosen_construction(Cat(), "oscar-covered-schemes", (), _OscarCoveredSchemesCategory),
    )


def _scheme_open_category(presentation: FiniteAffineGluing) -> SchemeOpenCategory:
    return cast(
        SchemeOpenCategory,
        chosen_construction(
            Cat(),
            "finite-gluing-open-category",
            (presentation,),
            lambda: SchemeOpenCategory(presentation),
        ),
    )


def _affine_open_from_equations(
    presentation: FiniteAffineGluing,
    chart_index: int,
    equations: tuple[CategoryOfCategories.ElementType, ...],
) -> AffineOpenCategory.ObjectType:
    chart = presentation.charts[chart_index]
    opens, _ = affine_structure_sheaf(chart)
    root = opens.root()
    match equations:
        case ():
            pieces = (opens.principal_open(root, chart.coordinate_ring().one()),)
        case _:
            pieces = tuple(opens.principal_open(root, equation) for equation in equations)
    return opens.finite_union(pieces)


def _finite_chart_preimage_affine_open(
    presentation: FiniteAffineGluing,
    source_chart: int,
    target_chart: int,
    target_open: AffineOpenCategory.ObjectType,
) -> AffineOpenCategory.ObjectType:
    match source_chart == target_chart:
        case True:
            return target_open
        case False:
            equations = _backend.finite_chart_preimage_equations(
                presentation,
                source_chart,
                target_open,
            )
            return _affine_open_from_equations(presentation, source_chart, equations)


def _component_intersection_open(
    presentation: FiniteAffineGluing,
    source_chart: int,
    source_open: AffineOpenCategory.ObjectType,
    target_open: AffineOpenCategory.ObjectType,
) -> AffineOpenCategory.ObjectType:
    equations = _backend.finite_component_intersection_equations(
        presentation,
        source_chart,
        source_open,
        target_open,
    )
    return _affine_open_from_equations(presentation, source_chart, equations)


def _compatible_sections_ring(
    open_object: SchemeOpenCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    """The equalizer ring of compatible sections on a chart-local open family."""

    def construct() -> CategoryOfCategories.ElementType:
        presentation = open_object.presentation()
        chart_opens = open_object.chart_opens()
        local_rings = tuple(component.section_ring() for component in chart_opens)

        def member(value: Hashable):
            match value:
                case (owner, values) if owner is open_object and isinstance(values, tuple):
                    match len(values) == len(local_rings):
                        case False:
                            return false
                        case True:
                            pass
                    for section, ring in zip(values, local_rings, strict=True):
                        match isinstance(section, CategoryOfCategories.ElementType) and section.parent() is ring:
                            case False:
                                return false
                            case True:
                                pass
                    for left in range(len(chart_opens)):
                        for right in range(left + 1, len(chart_opens)):
                            intersection = _component_intersection_open(
                                presentation,
                                left,
                                chart_opens[left],
                                chart_opens[right],
                            )
                            left_restriction = intersection.restriction_to(chart_opens[left])
                            right_restriction = _backend.finite_open_restriction(
                                presentation,
                                intersection,
                                chart_opens[right],
                            )
                            match ask(
                                left_restriction(values[left])
                                == right_restriction(values[right])
                            ):
                                case True:
                                    pass
                                case _:
                                    return false
                    return true
                case _:
                    return false

        carrier = Sets.from_membership(member)

        def add(pair: tuple[Hashable, Hashable]) -> Hashable:
            left, right = pair
            left_owner, left_values = cast(tuple[object, tuple[Any, ...]], left)
            right_owner, right_values = cast(tuple[object, tuple[Any, ...]], right)
            assert left_owner is open_object and right_owner is open_object
            return (
                open_object,
                tuple(a + b for a, b in zip(left_values, right_values, strict=True)),
            )

        def multiply(pair: tuple[Hashable, Hashable]) -> Hashable:
            left, right = pair
            left_owner, left_values = cast(tuple[object, tuple[Any, ...]], left)
            right_owner, right_values = cast(tuple[object, tuple[Any, ...]], right)
            assert left_owner is open_object and right_owner is open_object
            return (
                open_object,
                tuple(a * b for a, b in zip(left_values, right_values, strict=True)),
            )

        zero = (open_object, tuple(ring.zero() for ring in local_rings))
        one = (open_object, tuple(ring.one() for ring in local_rings))
        return certified_commutative_ring(carrier, add, multiply, zero, one)

    return chosen_construction(
        _rings(),
        "compatible-section-ring",
        (open_object,),
        construct,
    )


def _compatible_sections_restriction(
    smaller: SchemeOpenCategory.ObjectType,
    larger: SchemeOpenCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    source_ring = larger.section_ring()
    target_ring = smaller.section_ring()
    source_carrier = Rings(Sets).forgetful().on_object(source_ring)
    target_carrier = Rings(Sets).forgetful().on_object(target_ring)
    restrictions = tuple(
        small.restriction_to(large)
        for small, large in zip(smaller.chart_opens(), larger.chart_opens(), strict=True)
    )

    def rule(value: Hashable) -> Hashable:
        owner, sections = cast(tuple[object, tuple[Any, ...]], value)
        assert owner is larger
        return (
            smaller,
            tuple(
                restriction(section)
                for restriction, section in zip(restrictions, sections, strict=True)
            ),
        )

    underlying = Mor(Sets)(source_carrier, target_carrier)(rule)
    ambient = Rings(Sets).homomorphism(source_ring, target_ring, underlying)
    return _rings().restrict_morphism(ambient)


def _compatible_section_projection(
    open_object: SchemeOpenCategory.ObjectType,
    chart_index: int,
) -> MorphismCategory.ObjectType:
    source_ring = open_object.section_ring()
    target_ring = open_object.chart_open(chart_index).section_ring()
    source_carrier = Rings(Sets).forgetful().on_object(source_ring)
    target_carrier = Rings(Sets).forgetful().on_object(target_ring)

    def rule(value: Hashable) -> Hashable:
        owner, sections = cast(tuple[object, tuple[Any, ...]], value)
        assert owner is open_object
        return cast(CategoryOfCategories.ElementType, sections[chart_index]).datum()

    underlying = Mor(Sets)(source_carrier, target_carrier)(rule)
    ambient = Rings(Sets).homomorphism(source_ring, target_ring, underlying)
    return _rings().restrict_morphism(ambient)


def _compatible_section_lift(
    open_object: SchemeOpenCategory.ObjectType,
    chart_index: int,
) -> MorphismCategory.ObjectType:
    """Recover a compatible global section family from one chart section."""
    presentation = open_object.presentation()
    source_open = open_object.chart_open(chart_index)
    source_ring = source_open.section_ring()
    target_ring = open_object.section_ring()
    source_carrier = Rings(Sets).forgetful().on_object(source_ring)
    target_carrier = Rings(Sets).forgetful().on_object(target_ring)
    component_maps = tuple(
        component.restriction_to(source_open)
        if index == chart_index
        else _backend.finite_open_restriction(presentation, component, source_open)
        for index, component in enumerate(open_object.chart_opens())
    )

    def rule(value: Hashable) -> Hashable:
        section = source_ring.point(value)
        return (
            open_object,
            tuple(component_map(section) for component_map in component_maps),
        )

    underlying = Mor(Sets)(source_carrier, target_carrier)(rule)
    ambient = Rings(Sets).homomorphism(source_ring, target_ring, underlying)
    lift = _rings().restrict_morphism(ambient)
    projection = _compatible_section_projection(open_object, chart_index)
    _rings().retain_inverses(projection, lift)
    return lift


def _finite_chart_structure_sheaf_comparison(
    presentation: FiniteAffineGluing,
    chart_index: int,
) -> NaturalTransformation:
    """The retained isomorphism from the glued sheaf restricted to one chart to its affine sheaf."""

    def construct() -> NaturalTransformation:
        chart = presentation.charts[chart_index]
        local_opens, local_sheaf = affine_structure_sheaf(chart)
        scheme_opens = _scheme_open_category(presentation)

        def global_open(
            open_object: CategoryOfCategories.ElementType,
        ) -> SchemeOpenCategory.ObjectType:
            return scheme_opens.open(
                chart_index,
                cast(AffineOpenCategory.ObjectType, open_object),
            )

        def on_object(
            open_object: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            return global_open(open_object).section_ring()

        def on_morphism(
            opposite_inclusion: MorphismCategory.ObjectType,
        ) -> MorphismCategory.ObjectType:
            inclusion = opposite_morphism(opposite_inclusion)
            smaller = global_open(inclusion.domain())
            larger = global_open(inclusion.codomain())
            return smaller.restriction_to(larger)

        restricted_glued_sheaf = Fun(local_opens.op(), _rings())(
            on_object,
            on_morphism,
        )
        return natural_isomorphism(
            restricted_glued_sheaf,
            local_sheaf.functor,
            lambda open_object: _compatible_section_projection(
                global_open(open_object),
                chart_index,
            ),
            lambda open_object: _compatible_section_lift(
                global_open(open_object),
                chart_index,
            ),
        )

    return cast(
        NaturalTransformation,
        chosen_construction(
            Schemes(),
            "finite-chart-structure-sheaf-comparison",
            (presentation, chart_index),
            construct,
        ),
    )


def _affine_chart_structure_sheaf_comparison(
    affine: AffineSchemesCategory.ObjectType,
) -> NaturalTransformation:
    """The identity comparison for the one-chart affine presentation."""
    sheaf = affine_structure_sheaf(affine)[1].functor

    def identity(open_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ring = sheaf.on_object(open_object)
        return Mor(_rings())(ring, ring).one()

    return natural_isomorphism(sheaf, sheaf, identity, identity)


def _point_in_overlap_piece(
    point: AffineSpectrumPoint,
    open_object: AffineOpenCategory.ObjectType,
) -> bool:
    element = open_object.localizing_element()
    assert element is not None, "overlap pieces must be principal opens"
    return not prime_contains(point.prime, element)


def _transport_overlap_point(
    point: AffineSpectrumPoint,
    source_open: AffineOpenCategory.ObjectType,
    target_open: AffineOpenCategory.ObjectType,
    pullback: MorphismCategory.ObjectType,
) -> AffineSpectrumPoint:
    source_root = affine_structure_sheaf(point.scheme)[0].root()
    target_scheme = target_open.scheme()
    target_root = affine_structure_sheaf(target_scheme)[0].root()
    source_prime = prime_ideal_extension(source_open.restriction_to(source_root), point.prime)
    target_open_prime = prime_ideal_preimage(pullback, source_prime)
    target_prime = prime_ideal_preimage(target_open.restriction_to(target_root), target_open_prime)
    return AffineSchemes().spectrum_point(target_scheme, prime_generators(target_prime))


def _transition_point(
    presentation: FiniteAffineGluing,
    source: int,
    target: int,
    point: AffineSpectrumPoint,
) -> AffineSpectrumPoint | None:
    match source == target:
        case True:
            return point
        case False:
            pass
    overlap = presentation.overlap(source, target)
    match source == overlap.left:
        case True:
            for piece in overlap.pieces:
                match _point_in_overlap_piece(point, piece.left_open):
                    case True:
                        return _transport_overlap_point(
                            point,
                            piece.left_open,
                            piece.right_open,
                            piece.left_to_right_pullback,
                        )
                    case False:
                        pass
        case False:
            for piece in overlap.pieces:
                match _point_in_overlap_piece(point, piece.right_open):
                    case True:
                        return _transport_overlap_point(
                            point,
                            piece.right_open,
                            piece.left_open,
                            piece.right_to_left_pullback,
                        )
                    case False:
                        pass
    return None


def _finite_glued_point_quotient(
    presentation: FiniteAffineGluing,
):
    def construct():
        def member(value: Hashable):
            match value:
                case _TaggedAffinePoint(presentation=retained, chart=chart, point=point):
                    match retained is presentation and 0 <= chart < len(presentation.charts):
                        case True:
                            return true if point.scheme is presentation.charts[chart] else false
                        case False:
                            return false
                case _:
                    return false

        ambient = Sets.from_membership(member)

        def equivalent(
            first: CategoryOfCategories.ElementType,
            second: CategoryOfCategories.ElementType,
        ):
            left = cast(_TaggedAffinePoint, first.datum())
            right = cast(_TaggedAffinePoint, second.datum())
            match left.chart == right.chart:
                case True:
                    return true if prime_ideal_equal(left.point.prime, right.point.prime) else false
                case False:
                    pass
            transported = _transition_point(
                presentation,
                left.chart,
                right.chart,
                left.point,
            )
            match transported:
                case None:
                    return false
                case _:
                    return true if prime_ideal_equal(transported.prime, right.point.prime) else false

        quotient, projection = Sets.quotient(ambient, equivalent)
        return ambient, quotient, projection

    return chosen_construction(
        Sets,
        "finite-gluing-point-quotient",
        (presentation,),
        construct,
    )


def _finite_glued_topological_space(
    presentation: FiniteAffineGluing,
) -> TopologicalSpacesCategory.ObjectType[SchemeOpenCategory.ObjectType]:
    def construct() -> TopologicalSpacesCategory.ObjectType[SchemeOpenCategory.ObjectType]:
        _ambient, carrier, _projection = _finite_glued_point_quotient(presentation)
        opens = _scheme_open_category(presentation)

        def open_member(value: Hashable):
            match isinstance(value, SchemeOpenCategory.ObjectType):
                case True:
                    return true if value.presentation() is presentation else false
                case False:
                    return false

        open_carrier = Sets.from_membership(open_member)

        def open_point(key: SchemeOpenCategory.ObjectType) -> CategoryOfCategories.ElementType:
            assert key.presentation() is presentation
            return cast(CategoryOfCategories.ElementType, cast(Any, open_carrier).point(key))

        return TopologicalSpaces().from_open_category(
            carrier,
            open_carrier,
            opens,
            open_point,
            lambda key: key,
        )

    return cast(
        TopologicalSpacesCategory.ObjectType[SchemeOpenCategory.ObjectType],
        chosen_construction(
            TopologicalSpaces(),
            "finite-glued-topological-space",
            (presentation,),
            construct,
        ),
    )


def _finite_glued_structure_sheaf(
    presentation: FiniteAffineGluing,
) -> RingSheaf[SchemeOpenCategory.ObjectType]:
    def construct() -> RingSheaf[SchemeOpenCategory.ObjectType]:
        opens = _scheme_open_category(presentation)

        def on_object(open_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            return cast(SchemeOpenCategory.ObjectType, open_object).section_ring()

        def on_morphism(opposite_inclusion: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            inclusion = opposite_morphism(opposite_inclusion)
            smaller = cast(SchemeOpenCategory.ObjectType, inclusion.domain())
            larger = cast(SchemeOpenCategory.ObjectType, inclusion.codomain())
            return smaller.restriction_to(larger)

        functor = Fun(opens.op(), _rings())(on_object, on_morphism)
        presheaf = ring_presheaf_from_functor(
            _finite_glued_topological_space(presentation),
            opens,
            functor,
            lambda key: key,
            lambda open_object: open_object,
        )
        return ring_sheaf(presheaf)

    return cast(
        RingSheaf[SchemeOpenCategory.ObjectType],
        chosen_construction(
            Schemes(),
            "finite-glued-structure-sheaf",
            (presentation,),
            construct,
        ),
    )


def _finite_glued_ringed_space(
    presentation: FiniteAffineGluing,
) -> RingedSpacesCategory.ObjectType[SchemeOpenCategory.ObjectType]:
    return cast(
        RingedSpacesCategory.ObjectType[SchemeOpenCategory.ObjectType],
        chosen_construction(
            Schemes(),
            "finite-glued-ringed-space",
            (presentation,),
            lambda: RingedSpaces()(
                _finite_glued_topological_space(presentation),
                _finite_glued_structure_sheaf(presentation),
            ),
        ),
    )


def _quotient_tag(point: CategoryOfCategories.ElementType) -> _TaggedAffinePoint:
    representative = Sets.quotient_representative(point)
    datum = representative.datum()
    assert isinstance(datum, _TaggedAffinePoint)
    return datum


def _finite_glued_locally_ringed_space(
    presentation: FiniteAffineGluing,
) -> LocallyRingedSpacesCategory.ObjectType:
    def construct() -> LocallyRingedSpacesCategory.ObjectType:
        return LocallyRingedSpaces().with_stalks(
            _finite_glued_ringed_space(presentation),
            lambda point: _quotient_tag(point).point.local_ring,
            lambda _point, _stalk: true,
        )

    return cast(
        LocallyRingedSpacesCategory.ObjectType,
        chosen_construction(
            Schemes(),
            "finite-glued-locally-ringed-space",
            (presentation,),
            construct,
        ),
    )


def _finite_chart_preimage_open(
    presentation: FiniteAffineGluing,
    source_chart: int,
    target_open: SchemeOpenCategory.ObjectType,
) -> AffineOpenCategory.ObjectType:
    assert target_open.presentation() is presentation
    return target_open.chart_open(source_chart)


def _finite_chart_continuous_map(
    presentation: FiniteAffineGluing,
    chart_index: int,
) -> TopologicalSpacesCategory.MorphismType:
    def construct() -> TopologicalSpacesCategory.MorphismType:
        chart = presentation.charts[chart_index]
        source = affine_topological_space(chart)
        target = _finite_glued_topological_space(presentation)
        source_opens, _ = affine_structure_sheaf(chart)
        target_opens = _scheme_open_category(presentation)
        ambient, _quotient, projection = _finite_glued_point_quotient(presentation)

        def point_image(value: Hashable) -> Hashable:
            assert isinstance(value, AffineSpectrumPoint)
            tagged = _TaggedAffinePoint(presentation, chart_index, value)
            return projection(ambient.point(tagged)).datum()

        underlying = Mor(Sets)(source.carrier(), target.carrier())(point_image)

        def preimage(
            open_object: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            return _finite_chart_preimage_open(
                presentation,
                chart_index,
                cast(SchemeOpenCategory.ObjectType, open_object),
            )

        inverse = Fun(target_opens, source_opens)(
            preimage,
            lambda inclusion: Mor(source_opens)(
                preimage(inclusion.domain()),
                preimage(inclusion.codomain()),
            )(),
        )
        return TopologicalSpaces().morphism_with_inverse_image(
            source,
            target,
            underlying,
            inverse,
        )

    return cast(
        TopologicalSpacesCategory.MorphismType,
        chosen_construction(
            Schemes(),
            "finite-gluing-chart-continuous-map",
            (presentation, chart_index),
            construct,
        ),
    )


def _finite_chart_ringed_map(
    presentation: FiniteAffineGluing,
    chart_index: int,
) -> RingedSpacesCategory.MorphismType:
    def construct() -> RingedSpacesCategory.MorphismType:
        chart = presentation.charts[chart_index]
        source = affine_locally_ringed_space(chart).ringed_space()
        target = _finite_glued_ringed_space(presentation)
        continuous = _finite_chart_continuous_map(presentation, chart_index)

        def sheaf_map(open_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            target_open = cast(SchemeOpenCategory.ObjectType, open_object)
            return _compatible_section_projection(target_open, chart_index)

        return RingedSpaces().homomorphism(
            source,
            target,
            continuous,
            sheaf_map,
        )

    return cast(
        RingedSpacesCategory.MorphismType,
        chosen_construction(
            Schemes(),
            "finite-gluing-chart-ringed-map",
            (presentation, chart_index),
            construct,
        ),
    )


def _finite_chart_locally_ringed_map(
    presentation: FiniteAffineGluing,
    chart_index: int,
) -> LocallyRingedSpacesCategory.MorphismType:
    def construct() -> LocallyRingedSpacesCategory.MorphismType:
        chart = presentation.charts[chart_index]
        source = affine_locally_ringed_space(chart)
        target = _finite_glued_locally_ringed_space(presentation)

        def stalk_map(point: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            datum = point.datum()
            assert isinstance(datum, AffineSpectrumPoint)
            return Mor(_rings())(datum.local_ring, datum.local_ring).one()

        return LocallyRingedSpaces().homomorphism_with_stalks(
            source,
            target,
            _finite_chart_ringed_map(presentation, chart_index),
            stalk_map,
            lambda _point, _stalk_map: true,
        )

    return cast(
        LocallyRingedSpacesCategory.MorphismType,
        chosen_construction(
            Schemes(),
            "finite-gluing-chart-locally-ringed-map",
            (presentation, chart_index),
            construct,
        ),
    )


def _gluing_mediator_continuous_map(
    source: SchemesCategory.ObjectType,
    target: SchemesCategory.ObjectType,
    chart_maps: tuple[SchemesCategory.MorphismType, ...],
) -> TopologicalSpacesCategory.MorphismType:
    presentation = source.finite_affine_gluing()

    def construct() -> TopologicalSpacesCategory.MorphismType:
        source_space = source.space()
        target_space = target.space()
        source_opens = _scheme_open_category(presentation)
        target_opens = target_space.open_category()

        def point_image(value: Hashable) -> Hashable:
            quotient_point = source_space.carrier().point(value)
            tagged = _quotient_tag(quotient_point)
            chart_space = affine_topological_space(presentation.charts[tagged.chart])
            chart_point = chart_space.carrier().point(tagged.point)
            image = chart_maps[tagged.chart].continuous_map().underlying_map()(chart_point)
            return image.datum()

        underlying = Mor(Sets)(source_space.carrier(), target_space.carrier())(point_image)

        def preimage(
            open_object: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            chart_opens = tuple(
                cast(
                    AffineOpenCategory.ObjectType,
                    mapping.continuous_map().inverse_image().on_object(open_object),
                )
                for mapping in chart_maps
            )
            return source_opens.from_chart_opens(chart_opens)

        inverse = Fun(target_opens, source_opens)(
            preimage,
            lambda inclusion: Mor(source_opens)(
                preimage(inclusion.domain()),
                preimage(inclusion.codomain()),
            )(),
        )
        return TopologicalSpaces().morphism_with_inverse_image(
            source_space,
            target_space,
            underlying,
            inverse,
        )

    return cast(
        TopologicalSpacesCategory.MorphismType,
        chosen_construction(
            Schemes(),
            "finite-gluing-mediator-continuous-map",
            (source, target, chart_maps),
            construct,
        ),
    )


def _gluing_mediator_ringed_map(
    source: SchemesCategory.ObjectType,
    target: SchemesCategory.ObjectType,
    chart_maps: tuple[SchemesCategory.MorphismType, ...],
) -> RingedSpacesCategory.MorphismType:
    continuous = _gluing_mediator_continuous_map(source, target, chart_maps)

    def construct() -> RingedSpacesCategory.MorphismType:
        target_presheaf = target.sheaf().presheaf

        def component(target_key: Hashable) -> MorphismCategory.ObjectType:
            target_open = target_presheaf.open_object(target_key)
            source_open = cast(
                SchemeOpenCategory.ObjectType,
                continuous.inverse_image().on_object(target_open),
            )
            target_ring = target_presheaf.section_ring(target_key)
            source_ring = source_open.section_ring()
            target_carrier = Rings(Sets).forgetful().on_object(target_ring)
            source_carrier = Rings(Sets).forgetful().on_object(source_ring)
            chart_components = tuple(
                mapping.sheaf_map().component(target_open)
                for mapping in chart_maps
            )

            def rule(value: Hashable) -> Hashable:
                target_section = target_ring.point(value)
                return (
                    source_open,
                    tuple(component_map(target_section) for component_map in chart_components),
                )

            underlying = Mor(Sets)(target_carrier, source_carrier)(rule)
            ambient = Rings(Sets).homomorphism(target_ring, source_ring, underlying)
            return _rings().restrict_morphism(ambient)

        return RingedSpaces().homomorphism(
            source.ringed_space(),
            target.ringed_space(),
            continuous,
            component,
        )

    return cast(
        RingedSpacesCategory.MorphismType,
        chosen_construction(
            Schemes(),
            "finite-gluing-mediator-ringed-map",
            (source, target, chart_maps),
            construct,
        ),
    )


def _gluing_mediator_locally_ringed_map(
    source: SchemesCategory.ObjectType,
    target: SchemesCategory.ObjectType,
    chart_maps: tuple[SchemesCategory.MorphismType, ...],
) -> LocallyRingedSpacesCategory.MorphismType:
    presentation = source.finite_affine_gluing()

    def chart_point(
        quotient_point: CategoryOfCategories.ElementType,
    ) -> tuple[int, CategoryOfCategories.ElementType]:
        tagged = _quotient_tag(quotient_point)
        space = affine_topological_space(presentation.charts[tagged.chart])
        return tagged.chart, space.carrier().point(tagged.point)

    def construct() -> LocallyRingedSpacesCategory.MorphismType:
        return LocallyRingedSpaces().homomorphism_with_stalks(
            source,
            target,
            _gluing_mediator_ringed_map(source, target, chart_maps),
            lambda point: chart_maps[chart_point(point)[0]].stalk_map(chart_point(point)[1]),
            lambda point, _stalk_map: chart_maps[chart_point(point)[0]].local_map_condition(
                chart_point(point)[1]
            ),
        )

    return cast(
        LocallyRingedSpacesCategory.MorphismType,
        chosen_construction(
            Schemes(),
            "finite-gluing-mediator-locally-ringed-map",
            (source, target, chart_maps),
            construct,
        ),
    )


class SchemesCategory(PropertySubcategory):
    """Schemes: locally ringed spaces equipped with a retained affine open cover."""

    _base_category_class_and_axiom = (LocallyRingedSpacesCategory, "Scheme")

    class ObjectType:
        def affine_cover(self) -> tuple[AffineOpenChart, ...]:
            return selected_value(Schemes(), "affine-cover", (self,))

        def local_affineness(self) -> tuple[AffineOpenChart, ...]:
            return self.affine_cover()

        def finite_affine_gluing(self) -> FiniteAffineGluing:
            return selected_value(Schemes(), "finite-affine-gluing", (self,))

        def underlying_points(self) -> CategoryOfCategories.ElementType:
            """The carrier of the underlying topological space; its points are not scheme-valued points."""
            return self.space().carrier()

        def valued_points(self, ring: CategoryOfCategories.ElementType) -> MorphismCategory:
            """The exact Hom category whose objects are ``Spec(ring) -> self``."""
            return Schemes().valued_points(self, ring)

        def categorical_points(self) -> MorphismCategory:
            """The exact Hom category ``Mor(Schemes())(Spec(ZZ), self)``."""
            return Schemes().categorical_points(self)

        def over(
            self,
            base: SchemesCategory.ObjectType,
            structure_map: SchemesCategory.MorphismType,
        ) -> CategoryOfCategories.ElementType:
            """This scheme with a supplied structure map, as an ordinary object of the slice over ``base``."""
            return Schemes().over_base(self, base, structure_map)

    class ElementType:
        pass

    class MorphismType:
        pass

    def valued_points(
        self,
        scheme: SchemesCategory.ObjectType,
        ring: CategoryOfCategories.ElementType,
    ) -> MorphismCategory:
        """The fixed Hom category of ``ring``-valued points ``Spec(ring) -> scheme``."""
        assert scheme in self and ring in _rings()
        source = self.affine(cast(AffineSchemesCategory.ObjectType, Spec.on_object(ring)))
        return Mor(self)(source, scheme)

    def categorical_points(
        self,
        scheme: SchemesCategory.ObjectType,
    ) -> MorphismCategory:
        """The fixed Hom category of categorical points ``Spec(ZZ) -> scheme``."""
        return self.valued_points(scheme, integer_ring())

    def over_base(
        self,
        scheme: SchemesCategory.ObjectType,
        base: SchemesCategory.ObjectType,
        structure_map: SchemesCategory.MorphismType,
    ) -> CategoryOfCategories.ElementType:
        """Retain ``scheme -> base`` as the generic slice object over ``base``."""
        assert scheme in self and base in self
        assert structure_map.domain() is scheme and structure_map.codomain() is base
        return self.SliceOver(base)(structure_map)

    def retain_affine_cover(
        self,
        scheme: SchemesCategory.ObjectType,
        charts: tuple[AffineOpenChart, ...],
    ) -> None:
        assert scheme in self
        assert charts
        for chart in charts:
            source = affine_locally_ringed_space(chart.affine)
            assert chart.open_immersion.domain() is source
            assert chart.open_immersion.codomain() is scheme
        select_value(self, "affine-cover", (scheme,), charts)

    def affine_overlap(
        self,
        charts: tuple[AffineSchemesCategory.ObjectType, ...],
        left: int,
        right: int,
        pieces: tuple[AffineOverlapPiece, ...],
    ) -> AffineOverlap:
        """One pairwise overlap, retaining every affine member of its finite cover."""
        assert 0 <= left < right < len(charts)
        assert pieces, "an overlap cover needs at least one affine piece"
        left_opens, _ = affine_structure_sheaf(charts[left])
        right_opens, _ = affine_structure_sheaf(charts[right])
        left_root, right_root = left_opens.root(), right_opens.root()
        for piece in pieces:
            assert piece.left_open.scheme() is charts[left]
            assert piece.right_open.scheme() is charts[right]
            assert piece.left_open.parent_open() is left_root
            assert piece.right_open.parent_open() is right_root
            assert piece.left_to_right_pullback.domain() is piece.right_open.section_ring()
            assert piece.left_to_right_pullback.codomain() is piece.left_open.section_ring()
            assert piece.right_to_left_pullback.domain() is piece.left_open.section_ring()
            assert piece.right_to_left_pullback.codomain() is piece.right_open.section_ring()
        return AffineOverlap(
            left,
            right,
            pieces,
            left_opens.finite_union(tuple(piece.left_open for piece in pieces)),
            right_opens.finite_union(tuple(piece.right_open for piece in pieces)),
        )

    def glue_affines(
        self,
        charts: tuple[AffineSchemesCategory.ObjectType, ...],
        overlaps: tuple[AffineOverlap, ...],
    ) -> SchemesCategory.ObjectType:
        """Glue a finite affine family along represented overlap covers satisfying cocycle."""
        assert len(charts) >= 2
        expected_pairs = {
            (left, right)
            for left in range(len(charts))
            for right in range(left + 1, len(charts))
        }
        assert {(overlap.left, overlap.right) for overlap in overlaps} == expected_pairs
        presentation = FiniteAffineGluing(charts, overlaps)

        def construct() -> SchemesCategory.ObjectType:
            _backend.prepare_finite_gluing(presentation)
            for overlap in overlaps:
                for piece in overlap.pieces:
                    _rings().retain_inverses(
                        piece.left_to_right_pullback,
                        piece.right_to_left_pullback,
                    )
            value = cast(
                SchemesCategory.ObjectType,
                _finite_glued_locally_ringed_space(presentation),
            )
            assume(self.predicate()(value))
            _backend.retain_finite_glued_scheme(self, value, presentation)
            select_value(self, "finite-affine-gluing", (value,), presentation)
            chart_entries: list[AffineOpenChart] = []
            for chart_index, chart in enumerate(charts):
                source = self.affine(chart)
                ambient = _finite_chart_locally_ringed_map(presentation, chart_index)
                assert ambient.domain() is source and ambient.codomain() is value
                inclusion = cast(SchemesCategory.MorphismType, self.restrict_morphism(ambient))
                _backend.retain_chart_inclusion(inclusion, chart, value)
                chart_entries.append(
                    AffineOpenChart(
                        chart,
                        inclusion,
                        _finite_chart_structure_sheaf_comparison(
                            presentation, chart_index
                        ),
                    )
                )
            self.retain_affine_cover(value, tuple(chart_entries))
            return value

        return chosen_construction(
            self,
            "finite-affine-gluing",
            (charts, overlaps),
            construct,
        )

    def gluing_mediator(
        self,
        source: SchemesCategory.ObjectType,
        target: SchemesCategory.ObjectType,
        chart_maps: tuple[SchemesCategory.MorphismType, ...],
    ) -> SchemesCategory.MorphismType:
        """The unique scheme morphism induced by compatible maps on a finite affine cover."""
        presentation = source.finite_affine_gluing()
        assert len(chart_maps) == len(presentation.charts)
        for chart, mapping in zip(presentation.charts, chart_maps, strict=True):
            assert mapping.domain() is self.affine(chart)
            assert mapping.codomain() is target

        def construct() -> SchemesCategory.MorphismType:
            ambient = _gluing_mediator_locally_ringed_map(source, target, chart_maps)
            assert ambient.domain() is source and ambient.codomain() is target
            arrow = cast(SchemesCategory.MorphismType, self.restrict_morphism(ambient))
            _backend.retain_finite_gluing_mediator(
                arrow,
                source,
                target,
                tuple(cast(MorphismCategory.ObjectType, mapping) for mapping in chart_maps),
            )
            return arrow

        return chosen_construction(
            self,
            "finite-gluing-mediator",
            (source, target, chart_maps),
            construct,
        )

    def affine(self, affine: AffineSchemesCategory.ObjectType) -> SchemesCategory.ObjectType:
        def construct() -> SchemesCategory.ObjectType:
            value = cast(SchemesCategory.ObjectType, affine_locally_ringed_space(affine))
            assume(self.predicate()(value))
            inclusion = Mor(self)(value, value).one()
            self.retain_affine_cover(
                value,
                (
                    AffineOpenChart(
                        affine,
                        inclusion,
                        _affine_chart_structure_sheaf_comparison(affine),
                    ),
                ),
            )
            construction = _AffineSchemeConstruction(affine)
            _backend.retain_affine(
                self,
                cast(CategoryOfCategories.ElementType, value),
                cast(CategoryOfCategories.ElementType, affine),
                construction,
            )
            return value

        return chosen_construction(self, "affine-scheme", (affine,), construct)

    def affine_morphism(
        self,
        mapping: AffineSchemesCategory.MorphismType,
    ) -> SchemesCategory.MorphismType:
        def construct() -> SchemesCategory.MorphismType:
            source = self.affine(mapping.domain())
            target = self.affine(mapping.codomain())
            ambient = affine_locally_ringed_map(mapping)
            assert ambient.domain() is source and ambient.codomain() is target
            arrow = cast(SchemesCategory.MorphismType, self.restrict_morphism(ambient))
            _backend.retain_chart_map(
                cast(MorphismCategory.ObjectType, arrow),
                cast(CategoryOfCategories.ElementType, mapping.domain()),
                cast(CategoryOfCategories.ElementType, target),
                cast(CategoryOfCategories.ElementType, mapping.codomain()),
                mapping.pullback(),
            )
            return arrow

        return chosen_construction(self, "affine-morphism", (mapping,), construct)

    def to_locally_ringed_spaces(self) -> Functor:
        return self.subcategory_monomorphism()

    def to_ringed_spaces(self) -> Functor:
        return cast(
            Functor,
            chosen_construction(
                self,
                "to-ringed-spaces",
                (),
                lambda: LocallyRingedSpaces().to_ringed_spaces() * self.to_locally_ringed_spaces(),
            ),
        )

    def to_topological_spaces(self) -> Functor:
        return cast(
            Functor,
            chosen_construction(
                self,
                "to-topological-spaces",
                (),
                lambda: RingedSpaces().to_spaces() * self.to_ringed_spaces(),
            ),
        )

    def __repr__(self) -> str:
        return "Schemes"


def Schemes() -> SchemesCategory:
    return cast(SchemesCategory, LocallyRingedSpaces().Scheme())


_SCHEMES = Schemes()
AffineToSchemes: Functor = Fun(AffineSchemes(), _SCHEMES)(
    _SCHEMES.affine,
    _SCHEMES.affine_morphism,
)


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
    glued: _OscarCoveredSchemesCategory.ObjectType,
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
    schemes = _covered_schemes()
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
    schemes = _covered_schemes()
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
