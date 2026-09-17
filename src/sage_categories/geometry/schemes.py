"""Schemes represented by OSCAR covered schemes and retained affine gluings."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from typing import Any, cast

from sympy import false, true

from sage_categories.algebra.commutative_rings import (
    integer_ring,
    inverse_unit,
    localization_extension,
    polynomial_coefficient_map,
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
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.leaf_categories import ParameterizedThinCategory
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import assume
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.slices import SliceLikeCategory
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
    RingSheaf,
    descent_chart_comparison,
    descent_lift,
    descent_map,
    descent_projection,
    descent_restriction,
    descent_section_ring,
    identity_sheaf_comparison,
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
    "SchemeOpenCategory",
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
    open_immersion: SchemesCategory.MorphismType
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
            chart_opens = self.chart_opens()
            local_rings = tuple(component.section_ring() for component in chart_opens)

            def overlap_restrictions(
                left: int, right: int
            ) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
                return _backend.finite_overlap_restrictions(
                    self.presentation(),
                    left,
                    chart_opens[left],
                    right,
                    chart_opens[right],
                )

            return descent_section_ring(self, local_rings, overlap_restrictions)


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
                return descent_restriction(
                    larger,
                    smaller,
                    larger.section_ring(),
                    smaller.section_ring(),
                    tuple(
                        small.restriction_to(large)
                        for small, large in zip(
                            smaller.chart_opens(),
                            larger.chart_opens(),
                            strict=True,
                        )
                    ),
                )

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
class ProjectiveLinePresentation:
    """The standard finite affine presentation of a scheme over its supplied field."""

    scheme: SchemesCategory.ObjectType[SchemeOpenCategory.ObjectType]
    left_chart: AffineSchemesCategory.ObjectType
    right_chart: AffineSchemesCategory.ObjectType
    left_coordinate: CategoryOfCategories.ElementType
    right_coordinate: CategoryOfCategories.ElementType
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_inclusion: SchemesCategory.MorphismType
    right_inclusion: SchemesCategory.MorphismType
    chart_swap: SchemesCategory.MorphismType
    structure_sheaf: RingSheaf[SchemeOpenCategory.ObjectType]
    overlap_swap: MorphismCategory.ObjectType
    left_scheme_open: SchemeOpenCategory.ObjectType
    right_scheme_open: SchemeOpenCategory.ObjectType
    overlap_scheme_open: SchemeOpenCategory.ObjectType
    base: SchemesCategory.ObjectType[AffineOpenCategory.ObjectType]
    structure_map: SchemesCategory.MorphismType
    over_base: SliceLikeCategory.ObjectType
    swap_over_base: SliceLikeCategory.MorphismType


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
    right_to_left: MorphismCategory.ObjectType
    left_to_right: MorphismCategory.ObjectType


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


def _finite_glued_topological_space(
    presentation: FiniteAffineGluing,
) -> TopologicalSpacesCategory.ObjectType[SchemeOpenCategory.ObjectType]:
    def construct() -> TopologicalSpacesCategory.ObjectType[
        SchemeOpenCategory.ObjectType
    ]:
        def member(value: Hashable):
            match value:
                case _TaggedAffinePoint(
                    presentation=retained, chart=chart, point=point
                ):
                    match retained is presentation and 0 <= chart < len(
                        presentation.charts
                    ):
                        case True:
                            return (
                                true
                                if point.scheme is presentation.charts[chart]
                                else false
                            )
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
                    return (
                        true
                        if prime_ideal_equal(left.point.prime, right.point.prime)
                        else false
                    )
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
                    return (
                        true
                        if prime_ideal_equal(transported.prime, right.point.prime)
                        else false
                    )

        opens = _scheme_open_category(presentation)

        def open_member(value: Hashable):
            match isinstance(value, SchemeOpenCategory.ObjectType):
                case True:
                    return true if value.presentation() is presentation else false
                case False:
                    return false

        open_carrier = Sets.from_membership(open_member)

        def open_point(
            key: SchemeOpenCategory.ObjectType,
        ) -> CategoryOfCategories.ElementType:
            assert key.presentation() is presentation
            return cast(
                CategoryOfCategories.ElementType, cast(Any, open_carrier).point(key)
            )

        return TopologicalSpaces().quotient_from_open_category(
            ambient,
            equivalent,
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
) -> LocallyRingedSpacesCategory.ObjectType[SchemeOpenCategory.ObjectType]:
    def construct() -> LocallyRingedSpacesCategory.ObjectType[SchemeOpenCategory.ObjectType]:
        return LocallyRingedSpaces().with_stalks(
            _finite_glued_ringed_space(presentation),
            lambda point: _quotient_tag(point).point.local_ring,
            lambda _point, _stalk: true,
        )

    return cast(
        LocallyRingedSpacesCategory.ObjectType[SchemeOpenCategory.ObjectType],
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

        def preimage(
            open_object: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            return _finite_chart_preimage_open(
                presentation,
                chart_index,
                cast(SchemeOpenCategory.ObjectType, open_object),
            )

        return TopologicalSpaces().quotient_chart_morphism(
            source,
            target,
            lambda value: _TaggedAffinePoint(
                presentation, chart_index, cast(AffineSpectrumPoint, value)
            ),
            preimage,
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

        def sheaf_map(
            open_object: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            target_open = cast(SchemeOpenCategory.ObjectType, open_object)
            return descent_projection(
                target_open,
                target_open.section_ring(),
                target_open.chart_open(chart_index).section_ring(),
                chart_index,
            )

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


class SchemesCategory(PropertySubcategory):
    """Schemes: locally ringed spaces equipped with a retained affine open cover."""

    _base_category_class_and_axiom = (LocallyRingedSpacesCategory, "Scheme")

    class ObjectType[OpenKey: Hashable = Hashable]:
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
        ) -> SliceLikeCategory.ObjectType:
            """This scheme with a supplied structure map, as an ordinary object of the slice over ``base``."""
            return Schemes().over_base(self, base, structure_map)

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
    ) -> SliceLikeCategory.ObjectType:
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
    ) -> SchemesCategory.ObjectType[SchemeOpenCategory.ObjectType]:
        """Glue a finite affine family along represented overlap covers satisfying cocycle."""
        assert len(charts) >= 2
        expected_pairs = {
            (left, right)
            for left in range(len(charts))
            for right in range(left + 1, len(charts))
        }
        assert {(overlap.left, overlap.right) for overlap in overlaps} == expected_pairs
        presentation = FiniteAffineGluing(charts, overlaps)

        def construct() -> SchemesCategory.ObjectType[SchemeOpenCategory.ObjectType]:
            _backend.prepare_finite_gluing(presentation)
            for overlap in overlaps:
                for piece in overlap.pieces:
                    _rings().retain_inverses(
                        piece.left_to_right_pullback,
                        piece.right_to_left_pullback,
                    )
            value = cast(
                SchemesCategory.ObjectType[SchemeOpenCategory.ObjectType],
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
                inclusion = cast(
                    SchemesCategory.MorphismType, self.restrict_morphism(ambient)
                )
                _backend.retain_chart_inclusion(inclusion, chart, value)
                local_opens, local_sheaf = affine_structure_sheaf(chart)
                scheme_opens = _scheme_open_category(presentation)

                def global_open(
                    open_object: CategoryOfCategories.ElementType,
                    *,
                    retained_chart_index: int = chart_index,
                    retained_scheme_opens: SchemeOpenCategory = scheme_opens,
                ) -> SchemeOpenCategory.ObjectType:
                    return retained_scheme_opens.open(
                        retained_chart_index,
                        cast(AffineOpenCategory.ObjectType, open_object),
                    )

                def projection(
                    global_key: Hashable,
                    *,
                    retained_chart_index: int = chart_index,
                ) -> MorphismCategory.ObjectType:
                    represented = cast(SchemeOpenCategory.ObjectType, global_key)
                    return descent_projection(
                        represented,
                        represented.section_ring(),
                        represented.chart_open(retained_chart_index).section_ring(),
                        retained_chart_index,
                    )

                def lift(
                    global_key: Hashable,
                    *,
                    retained_chart_index: int = chart_index,
                ) -> MorphismCategory.ObjectType:
                    represented = cast(SchemeOpenCategory.ObjectType, global_key)
                    source_open = represented.chart_open(retained_chart_index)
                    component_maps = tuple(
                        component.restriction_to(source_open)
                        if index == retained_chart_index
                        else _backend.finite_open_restriction(
                            presentation, component, source_open
                        )
                        for index, component in enumerate(represented.chart_opens())
                    )
                    return descent_lift(
                        represented,
                        source_open.section_ring(),
                        represented.section_ring(),
                        component_maps,
                        retained_chart_index,
                    )

                comparison = descent_chart_comparison(
                    local_opens,
                    local_sheaf,
                    global_open,
                    lambda key: cast(SchemeOpenCategory.ObjectType, key).section_ring(),
                    lambda smaller, larger: cast(
                        SchemeOpenCategory.ObjectType, smaller
                    ).restriction_to(cast(SchemeOpenCategory.ObjectType, larger)),
                    projection,
                    lift,
                )
                chart_entries.append(AffineOpenChart(chart, inclusion, comparison))
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
            source_opens = _scheme_open_category(presentation)

            def chart_point(
                quotient_point: CategoryOfCategories.ElementType,
            ) -> tuple[int, CategoryOfCategories.ElementType]:
                tagged = _quotient_tag(quotient_point)
                space = affine_topological_space(presentation.charts[tagged.chart])
                return tagged.chart, space.carrier().point(tagged.point)

            def assemble_open(
                chart_opens: tuple[CategoryOfCategories.ElementType, ...],
            ) -> CategoryOfCategories.ElementType:
                return source_opens.from_chart_opens(
                    tuple(
                        cast(AffineOpenCategory.ObjectType, open_object)
                        for open_object in chart_opens
                    )
                )

            continuous = TopologicalSpaces().quotient_mediator(
                source.space(),
                target.space(),
                tuple(mapping.continuous_map() for mapping in chart_maps),
                chart_point,
                assemble_open,
            )
            target_presheaf = target.sheaf().presheaf

            def sheaf_component(target_key: Hashable) -> MorphismCategory.ObjectType:
                target_open = target_presheaf.open_object(target_key)
                source_open = cast(
                    SchemeOpenCategory.ObjectType,
                    continuous.inverse_image().on_object(target_open),
                )
                return descent_map(
                    source_open,
                    target_presheaf.section_ring(target_key),
                    source_open.section_ring(),
                    tuple(
                        mapping.sheaf_map().component(target_open)
                        for mapping in chart_maps
                    ),
                )

            ringed = RingedSpaces().homomorphism(
                source.ringed_space(),
                target.ringed_space(),
                continuous,
                sheaf_component,
            )
            ambient = LocallyRingedSpaces().homomorphism_with_stalks(
                source,
                target,
                ringed,
                lambda point: chart_maps[chart_point(point)[0]].stalk_map(
                    chart_point(point)[1]
                ),
                lambda point, _stalk_map: chart_maps[
                    chart_point(point)[0]
                ].local_map_condition(chart_point(point)[1]),
            )
            arrow = cast(SchemesCategory.MorphismType, self.restrict_morphism(ambient))
            _backend.retain_covered_morphism(
                arrow,
                source,
                target,
                tuple(
                    cast(MorphismCategory.ObjectType, mapping) for mapping in chart_maps
                ),
            )
            return arrow

        return chosen_construction(
            self,
            "finite-gluing-mediator",
            (source, target, chart_maps),
            construct,
        )

    def affine(self, affine: AffineSchemesCategory.ObjectType) -> SchemesCategory.ObjectType[AffineOpenCategory.ObjectType]:
        def construct() -> SchemesCategory.ObjectType[AffineOpenCategory.ObjectType]:
            value = cast(SchemesCategory.ObjectType[AffineOpenCategory.ObjectType], affine_locally_ringed_space(affine))
            assume(self.predicate()(value))
            inclusion = Mor(self)(value, value).one()
            self.retain_affine_cover(
                value,
                (
                    AffineOpenChart(
                        affine,
                        inclusion,
                        identity_sheaf_comparison(affine_structure_sheaf(affine)[1]),
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
        localization_extension(right_overlap.section_ring(), left_overlap.section_ring(), right_to_left_base),
        localization_extension(left_overlap.section_ring(), right_overlap.section_ring(), left_to_right_base),
    )


def projective_line(
    field: CategoryOfCategories.ElementType,
) -> ProjectiveLinePresentation:
    """Glue the standard two charts of ``P^1`` through the general scheme owner.

    The gluing uses Stacks, Lemma 26.14.1 (01JB). The coordinate exchange is
    defined on the charts, descends through the checked mediator, and is its own
    inverse because the two chart coordinate exchanges are inverse maps.
    """
    cover = _projective_line_cover(field)
    schemes = Schemes()
    charts = (cover.left, cover.right)
    piece = AffineOverlapPiece(
        cover.left_overlap, cover.right_overlap,
        cover.right_to_left, cover.left_to_right,
    )
    overlap = schemes.affine_overlap(charts, 0, 1, (piece,))
    glued = schemes.glue_affines(charts, (overlap,))
    left_entry, right_entry = glued.affine_cover()
    left_inclusion, right_inclusion = left_entry.open_immersion, right_entry.open_immersion

    swap_left = schemes.affine_morphism(AffineSchemes().construct_morphism(
        cover.left, cover.right,
        presented_ring_homomorphism(cover.right_ring, cover.left_ring, (cover.t,)),
    ))
    swap_right = schemes.affine_morphism(AffineSchemes().construct_morphism(
        cover.right, cover.left,
        presented_ring_homomorphism(cover.left_ring, cover.right_ring, (cover.u,)),
    ))
    swap = schemes.gluing_mediator(
        glued, glued, (right_inclusion * swap_left, left_inclusion * swap_right),
    )
    schemes.retain_inverses(swap, swap)

    opens = _scheme_open_category(glued.finite_affine_gluing())
    left_global = opens.open(0, cover.left_root)
    right_global = opens.open(1, cover.right_root)
    overlap_global = opens.open(0, cover.left_overlap)
    pulled_overlap = swap.continuous_map().inverse_image().on_object(overlap_global)
    local_source = pulled_overlap.chart_open(0)
    # Read the overlap action from the actual sheaf map, not from a separately
    # constructed substitution that could disagree with the scheme morphism.
    overlap_swap = (
        cover.left_overlap.restriction_to(local_source)
        * descent_projection(pulled_overlap, pulled_overlap.section_ring(), local_source.section_ring(), 0)
        * swap.sheaf_map().component(overlap_global)
        * left_entry.structure_sheaf_comparison.inverse().component(cover.left_overlap)
    )
    _rings().retain_inverses(overlap_swap, overlap_swap)

    base_affine = Spec.on_object(field)
    base = schemes.affine(base_affine)
    structure_maps = tuple(
        schemes.affine_morphism(AffineSchemes().construct_morphism(
            chart, base_affine, polynomial_coefficient_map(chart.coordinate_ring()),
        ))
        for chart in charts
    )
    structure_map = schemes.gluing_mediator(glued, base, structure_maps)
    over_base = glued.over(base, structure_map)
    slice_category = schemes.SliceOver(base)
    swap_over_base = Mor(slice_category)(over_base, over_base)(swap)
    slice_category.retain_inverses(swap_over_base, swap_over_base)

    return ProjectiveLinePresentation(
        glued, cover.left, cover.right, cover.t, cover.u,
        cover.left_overlap, cover.right_overlap,
        left_inclusion, right_inclusion, swap, glued.sheaf(), overlap_swap,
        left_global, right_global, overlap_global,
        base, structure_map, over_base, swap_over_base,
    )
