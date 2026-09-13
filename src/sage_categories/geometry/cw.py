"""CW presentations of complex projective spaces and their sequential colimit."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from functools import cache
from typing import Any, cast

from sympy import false, true

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import cocone, cocones
from sage_categories.cat.declarations import Sets, omega
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.predicates import Predicate, Proposition, register_handler
from sage_categories.cat.shapes import Thin
from sage_categories.geometry.spaces import TopologicalSpaces, TopologicalSpacesCategory

__all__ = [
    "CWOpen",
    "ComplexProjectivePoint",
    "ProjectiveInfinityPresentation",
    "ProjectiveSpacePresentation",
    "complex_projective_point",
    "projective_infinity",
    "projective_space",
]


@dataclass(frozen=True, slots=True)
class ComplexProjectivePoint:
    """A normalized homogeneous-coordinate representative of a complex projective point."""

    coordinates: tuple[complex, ...]


def complex_projective_point(*coordinates: complex) -> ComplexProjectivePoint:
    """Return the projective point represented by nonzero homogeneous coordinates."""
    assert coordinates and any(value != 0 for value in coordinates)
    pivot = next(value for value in coordinates if value != 0)
    normalized = tuple(complex(value / pivot) for value in coordinates)
    return ComplexProjectivePoint(normalized)


@dataclass(frozen=True, eq=False, slots=True)
class CWOpen:
    """One certified open in a finite projective-space CW topology.

    ``contains`` is its point-membership rule.  ``subset_rule`` may decide inclusion
    into another retained open; an undecided comparison remains an undecided thin
    comparison rather than being replaced by a finite enumeration.
    """

    stage: int
    name: Hashable
    contains: Callable[[ComplexProjectivePoint], bool]
    subset_rule: Callable[[CWOpen], bool | None] | None = None

    def included_in(self, other: CWOpen) -> bool | None:
        return _named_open_inclusion(self, other, self.name, other.name, self.subset_rule)


@dataclass(frozen=True, eq=False, slots=True)
class _WeakCWOpen:
    """An open of the weak colimit topology via compatible opens on every stage."""

    presentation: ProjectiveInfinityPresentation
    stage_open_rule: Callable[[int], CWOpen]
    name: Hashable
    subset_rule: Callable[[_WeakCWOpen], bool | None] | None = None

    def stage_open(self, stage: int) -> CWOpen:
        result = self.stage_open_rule(stage)
        assert result.stage == stage
        return result

    def included_in(self, other: _WeakCWOpen) -> bool | None:
        return _named_open_inclusion(self, other, self.name, other.name, self.subset_rule)


def _named_open_inclusion[Open](
    first: Open,
    second: Open,
    first_name: Hashable,
    second_name: Hashable,
    subset_rule: Callable[[Open], bool | None] | None,
) -> bool | None:
    """The shared identity/empty/whole/custom-rule inclusion calculus for CW opens."""
    if first is second:
        return True
    match first_name, second_name:
        case ("empty", _) | (_, "whole"):
            return True
        case _:
            pass
    return None if subset_rule is None else subset_rule(second)


class _CWOpenIncludedPredicate(Predicate):
    name = "cw_open_included"


cw_open_included = _CWOpenIncludedPredicate()


def _open_inclusion_handler(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
) -> bool | None:
    left, right = cast(Any, first).datum(), cast(Any, second).datum()
    match left, right:
        case CWOpen(), CWOpen():
            return left.included_in(right)
        case _WeakCWOpen(), _WeakCWOpen():
            return left.included_in(right)
        case _:
            return None


register_handler(cw_open_included, _open_inclusion_handler)


def _open_order(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
) -> Proposition:
    return cw_open_included(first, second)


@dataclass(frozen=True, eq=False, slots=True)
class ProjectiveSpacePresentation:
    """The standard CW presentation of ``CP^stage``."""

    stage: int
    space: TopologicalSpacesCategory.ObjectType
    empty_open: CWOpen
    whole_open: CWOpen

    def cells(self) -> tuple[int, ...]:
        """The cell dimensions ``0,2,...,2*stage``."""
        return tuple(2 * index for index in range(self.stage + 1))

    def open(self, value: CWOpen) -> CategoryOfCategories.ElementType:
        assert value.stage == self.stage
        return self.space.open_object(value)

    def complex_conjugation(self) -> TopologicalSpacesCategory.MorphismType:
        """Complex conjugation on this finite skeleton."""
        return _stage_conjugation(self.stage)


def _stage_open_space(stage: int) -> tuple[CategoryOfCategories.ElementType, Any]:
    opens = Sets.from_membership(lambda value: true if isinstance(value, CWOpen) and value.stage == stage else false)
    category = Thin(opens, _open_order)
    return opens, category


def _cw_open_datum(open_object: CategoryOfCategories.ElementType) -> CWOpen:
    """Return the retained finite-stage open carried by one open-category object."""
    return _cw_open_datum(open_object)


def _weak_cw_open_datum(open_object: CategoryOfCategories.ElementType) -> _WeakCWOpen:
    """Return the retained weak-CW open carried by one open-category object."""
    return cast(_WeakCWOpen, cast(Any, open_object).point().datum())


@cache
def projective_space(stage: int) -> ProjectiveSpacePresentation:
    """Return ``CP^stage`` with its retained standard CW topology."""
    assert stage >= 0
    carrier = Sets.from_membership(lambda value: true if isinstance(value, ComplexProjectivePoint) and len(value.coordinates) == stage + 1 else false)
    opens, open_category = _stage_open_space(stage)
    empty = CWOpen(stage, "empty", lambda _: False)
    whole = CWOpen(stage, "whole", lambda _: True)

    def open_point(key: object) -> CategoryOfCategories.ElementType:
        assert isinstance(key, CWOpen) and key.stage == stage
        return cast(CategoryOfCategories.ElementType, cast(Any, opens).point(key))

    space = TopologicalSpaces().from_open_category(
        carrier,
        opens,
        open_category,
        open_point,
        lambda key: open_category(open_point(key)),
    )
    return ProjectiveSpacePresentation(stage, space, empty, whole)


def _pad_point(point: ComplexProjectivePoint, target_stage: int) -> ComplexProjectivePoint:
    assert len(point.coordinates) <= target_stage + 1
    padding = (0j,) * (target_stage + 1 - len(point.coordinates))
    return ComplexProjectivePoint((*point.coordinates, *padding))


def _restrict_open(open_set: CWOpen, source_stage: int) -> CWOpen:
    assert source_stage <= open_set.stage
    match source_stage == open_set.stage:
        case True:
            return open_set
        case False:
            return CWOpen(
                source_stage,
                ("restriction", open_set),
                lambda point: open_set.contains(_pad_point(point, open_set.stage)),
                lambda other: True if other.name == "whole" else None,
            )


def _conjugate_point(point: ComplexProjectivePoint) -> ComplexProjectivePoint:
    return complex_projective_point(*(value.conjugate() for value in point.coordinates))


@cache
def _stage_conjugation(stage: int) -> TopologicalSpacesCategory.MorphismType:
    presentation = projective_space(stage)
    underlying = Mor(Sets)(presentation.space.carrier(), presentation.space.carrier())(_conjugate_point)

    def preimage(
        open_object: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        open_set = _cw_open_datum(open_object)
        conjugate_open = CWOpen(
            stage,
            ("conjugate", open_set),
            lambda point: open_set.contains(_conjugate_point(point)),
            lambda other: True if other.name == "whole" else None,
        )
        return presentation.open(conjugate_open)

    inverse = Fun(presentation.space.open_category(), presentation.space.open_category())(
        preimage,
        lambda inclusion: Mor(presentation.space.open_category())(preimage(inclusion.domain()), preimage(inclusion.codomain()))(),
    )
    return TopologicalSpaces().morphism_with_inverse_image(
        presentation.space,
        presentation.space,
        underlying,
        inverse,
    )


@cache
def _standard_inclusion(source_stage: int, target_stage: int) -> TopologicalSpacesCategory.MorphismType:
    assert 0 <= source_stage <= target_stage
    source, target = projective_space(source_stage), projective_space(target_stage)
    underlying = Mor(Sets)(source.space.carrier(), target.space.carrier())(lambda point: _pad_point(point, target_stage))
    inverse = Fun(target.space.open_category(), source.space.open_category())(
        lambda target_open: source.open(_restrict_open(_cw_open_datum(target_open), source_stage)),
        lambda inclusion: Mor(source.space.open_category())(
            source.open(_restrict_open(_cw_open_datum(inclusion.domain()), source_stage)),
            source.open(_restrict_open(_cw_open_datum(inclusion.codomain()), source_stage)),
        )(),
    )
    return TopologicalSpaces().morphism_with_inverse_image(source.space, target.space, underlying, inverse)


@dataclass(frozen=True, eq=False, slots=True)
class ProjectiveInfinityPresentation:
    """The full sequential CW colimit ``CP^infinity``."""

    diagram: Functor
    space: TopologicalSpacesCategory.ObjectType
    weak_opens: CategoryOfCategories.ElementType
    empty_open: _WeakCWOpen
    whole_open: _WeakCWOpen

    def finite_skeleton(self, stage: int) -> ProjectiveSpacePresentation:
        return projective_space(stage)

    def structure_map(self, stage: int) -> TopologicalSpacesCategory.MorphismType:
        vertex = omega.object_at(omega.object_set().point(stage + 1))
        return cast(
            TopologicalSpacesCategory.MorphismType,
            TopologicalSpaces().Colimits(omega).universal_data(self.diagram).leg(vertex),
        )

    def open(self, value: _WeakCWOpen) -> CategoryOfCategories.ElementType:
        return self.space.open_object(value)

    def complex_conjugation(self) -> TopologicalSpacesCategory.MorphismType:
        """The map induced by the compatible conjugations on all finite skeleta."""
        candidate = cocones(self.diagram)(
            cocone(
                self.diagram,
                self.space,
                lambda vertex: self.structure_map(_diagram_stage(vertex)) * projective_space(_diagram_stage(vertex)).complex_conjugation(),
            )
        )
        return cast(
            TopologicalSpacesCategory.MorphismType,
            TopologicalSpaces().Colimits(omega).universal_data(self.diagram).lift(candidate),
        )


def _diagram_stage(vertex: CategoryOfCategories.ElementType) -> int:
    return int(cast(Any, vertex).point().datum()) - 1


def _projective_diagram() -> Functor:
    spaces = TopologicalSpaces()
    return Fun(omega, spaces)(
        lambda vertex: projective_space(_diagram_stage(vertex)).space,
        lambda arrow: _standard_inclusion(
            _diagram_stage(cast(Any, arrow).domain()),
            _diagram_stage(cast(Any, arrow).codomain()),
        ),
    )


def _weak_open_space(
    presentation: ProjectiveInfinityPresentation,
) -> tuple[CategoryOfCategories.ElementType, Any]:
    opens = Sets.from_membership(lambda value: true if isinstance(value, _WeakCWOpen) and value.presentation is presentation else false)
    return opens, Thin(opens, _open_order)


def _projective_infinity_leg(
    space: TopologicalSpacesCategory.ObjectType,
    set_colimit: Any,
    vertex: CategoryOfCategories.ElementType,
) -> TopologicalSpacesCategory.MorphismType:
    """Lift one finite-stage set-colimit leg to the weak CW topology."""
    stage = _diagram_stage(vertex)
    source = projective_space(stage)
    underlying = set_colimit.leg(vertex)
    inverse = Fun(space.open_category(), source.space.open_category())(
        lambda target_open: source.open(cast(_WeakCWOpen, _cw_open_datum(target_open)).stage_open(stage)),
        lambda inclusion: Mor(source.space.open_category())(
            source.open(cast(_WeakCWOpen, _cw_open_datum(inclusion.domain())).stage_open(stage)),
            source.open(cast(_WeakCWOpen, _cw_open_datum(inclusion.codomain())).stage_open(stage)),
        )(),
    )
    return TopologicalSpaces().morphism_with_inverse_image(source.space, space, underlying, inverse)


def _projective_infinity_preimage(
    presentation: ProjectiveInfinityPresentation,
    candidate: CategoryOfCategories.ElementType,
    target_open: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    """The weak-CW preimage of one open under a compatible cocone."""
    weak = _WeakCWOpen(
        presentation,
        lambda stage: cast(
            CWOpen,
            cast(
                Any,
                cast(
                    TopologicalSpacesCategory.MorphismType,
                    cast(Any, candidate).component(omega.object_at(omega.object_set().point(stage + 1))),
                )
                .inverse_image()
                .on_object(target_open),
            )
            .point()
            .datum(),
        ),
        ("preimage", target_open),
    )
    return presentation.open(weak)


def _projective_infinity_descent(
    presentation: ProjectiveInfinityPresentation,
    space: TopologicalSpacesCategory.ObjectType,
    underlying_diagram: Functor,
    set_colimit: Any,
    candidate: CategoryOfCategories.ElementType,
) -> TopologicalSpacesCategory.MorphismType:
    """Descend one compatible topological cocone through the weak CW colimit."""
    target = cast(TopologicalSpacesCategory.ObjectType, cast(Any, candidate).apex())
    set_candidate = cocones(underlying_diagram)(
        cocone(
            underlying_diagram,
            target.carrier(),
            lambda vertex: cast(
                TopologicalSpacesCategory.MorphismType,
                cast(Any, candidate).component(vertex),
            ).underlying_map(),
        )
    )
    underlying = set_colimit.lift(set_candidate)

    def preimage(target_open: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return _projective_infinity_preimage(presentation, candidate, target_open)

    inverse = Fun(target.open_category(), space.open_category())(
        preimage,
        lambda inclusion: Mor(space.open_category())(preimage(inclusion.domain()), preimage(inclusion.codomain()))(),
    )
    return TopologicalSpaces().morphism_with_inverse_image(space, target, underlying, inverse)


_projective_infinity: ProjectiveInfinityPresentation | None = None


def projective_infinity() -> ProjectiveInfinityPresentation:
    """Return the full CW colimit of the standard sequence of complex projective spaces."""
    global _projective_infinity
    match _projective_infinity:
        case ProjectiveInfinityPresentation():
            return _projective_infinity
        case None:
            pass

    spaces = TopologicalSpaces()
    diagram = _projective_diagram()
    underlying_diagram = Fun(omega, Sets)(
        lambda vertex: cast(TopologicalSpacesCategory.ObjectType, diagram.on_object(vertex)).carrier(),
        lambda arrow: cast(TopologicalSpacesCategory.MorphismType, diagram.on_morphism(arrow)).underlying_map(),
    )
    carrier = Sets.Colimits(omega)(underlying_diagram)

    presentation = ProjectiveInfinityPresentation.__new__(ProjectiveInfinityPresentation)
    object.__setattr__(presentation, "diagram", diagram)
    object.__setattr__(presentation, "space", cast(TopologicalSpacesCategory.ObjectType, None))
    object.__setattr__(presentation, "weak_opens", cast(CategoryOfCategories.ElementType, None))
    empty = _WeakCWOpen(
        presentation,
        lambda stage: projective_space(stage).empty_open,
        "empty",
    )
    whole = _WeakCWOpen(
        presentation,
        lambda stage: projective_space(stage).whole_open,
        "whole",
    )
    opens, open_category = _weak_open_space(presentation)

    def open_point(key: object) -> CategoryOfCategories.ElementType:
        assert isinstance(key, _WeakCWOpen) and key.presentation is presentation
        return cast(CategoryOfCategories.ElementType, cast(Any, opens).point(key))

    space = spaces.from_open_category(
        carrier,
        opens,
        open_category,
        open_point,
        lambda key: open_category(open_point(key)),
    )
    object.__setattr__(presentation, "space", space)
    object.__setattr__(presentation, "weak_opens", opens)
    object.__setattr__(presentation, "empty_open", empty)
    object.__setattr__(presentation, "whole_open", whole)
    _projective_infinity = presentation

    set_colimit = Sets.Colimits(omega).universal_data(underlying_diagram)

    spaces.Colimits(omega).with_universal_data(
        diagram,
        space,
        cocone(diagram, space, lambda vertex: _projective_infinity_leg(space, set_colimit, vertex)),
        lambda candidate: _projective_infinity_descent(presentation, space, underlying_diagram, set_colimit, candidate),
    )
    return presentation
