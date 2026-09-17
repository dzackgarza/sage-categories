"""Private OSCAR realization boundary for covered schemes."""

from __future__ import annotations

from typing import Any, cast

from sage_categories.algebra._firewall import commutative_rings as _rings_backend
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealization,
    NativeMorphismRealizations,
    NativeObjectRealization,
    NativeObjectRealizations,
)
from sage_categories.engines import oscar
from sage_categories.engines.julia_bridge import OscarHandle
from sage_categories.geometry._firewall import affine as _affine_backend

_objects: NativeObjectRealizations[OscarHandle, object] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[OscarHandle] = NativeMorphismRealizations()
_finite_gluing_presentations: dict[object, OscarHandle] = {}
_finite_gluing_edges: dict[tuple[object, int, int], OscarHandle] = {}


def _retain_object(owner: Category, value: CategoryOfCategories.ElementType, native: OscarHandle, construction: object) -> None:
    _objects.retain(owner, value, native, construction)


def native_scheme(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[OscarHandle, object]:
    return _objects.realization(value)


def scheme_handle(value: CategoryOfCategories.ElementType) -> OscarHandle:
    native = native_scheme(value).native
    assert isinstance(native, OscarHandle)
    return native


def retain_affine(owner: Category, value: CategoryOfCategories.ElementType, affine: CategoryOfCategories.ElementType, construction: object) -> None:
    _retain_object(owner, value, oscar.covered_scheme(_affine_backend.scheme_handle(affine)), construction)


def prepare_finite_gluing(presentation: object) -> None:
    """Build and validate the private OSCAR realization of a finite affine gluing."""
    match presentation in _finite_gluing_presentations:
        case True:
            return
        case False:
            pass
    charts = cast(Any, presentation).charts
    overlaps = cast(Any, presentation).overlaps
    native_charts = tuple(_affine_backend.scheme_handle(chart) for chart in charts)
    native_gluings: list[OscarHandle] = []
    for overlap in overlaps:
        pieces = overlap.pieces
        gluing = oscar.general_gluing(
            native_charts[overlap.left],
            native_charts[overlap.right],
            _affine_backend.open_handle(overlap.left_open),
            _affine_backend.open_handle(overlap.right_open),
            tuple(_affine_backend.open_handle(piece.left_open) for piece in pieces),
            tuple(_affine_backend.open_handle(piece.right_open) for piece in pieces),
            tuple(_rings_backend.oscar_morphism_handle(piece.left_to_right_pullback) for piece in pieces),
            tuple(_rings_backend.oscar_morphism_handle(piece.right_to_left_pullback) for piece in pieces),
        )
        _finite_gluing_edges[presentation, overlap.left, overlap.right] = gluing
        native_gluings.append(gluing)
    for left in range(len(charts)):
        for middle in range(left + 1, len(charts)):
            for right in range(middle + 1, len(charts)):
                assert oscar.gluing_cocycle(
                    _finite_gluing_edges[presentation, left, middle],
                    _finite_gluing_edges[presentation, middle, right],
                    _finite_gluing_edges[presentation, left, right],
                ), f"gluing cocycle fails on charts {(left, middle, right)!r}"
    _finite_gluing_presentations[presentation] = oscar.finite_covered_scheme(
        native_charts,
        tuple(native_gluings),
    )


def retain_finite_glued_scheme(
    owner: Category,
    value: CategoryOfCategories.ElementType,
    presentation: object,
) -> None:
    """Attach the checked finite-cover realization to the public scheme value."""
    prepare_finite_gluing(presentation)
    _retain_object(owner, value, _finite_gluing_presentations[presentation], presentation)


def finite_open_contains(
    presentation: object,
    smaller: object,
    larger: object,
) -> bool:
    """Decide containment of two chart-affine basis opens in the glued scheme."""
    prepare_finite_gluing(presentation)
    return oscar.covered_open_contains(
        _finite_gluing_presentations[presentation],
        _affine_backend.open_handle(smaller),
        _affine_backend.open_handle(larger),
    )


def finite_open_restriction(
    presentation: object,
    smaller: object,
    larger: object,
) -> MorphismCategory.ObjectType:
    """Reconstruct the covered structure-sheaf restriction on two basis opens."""
    prepare_finite_gluing(presentation)
    native = oscar.covered_open_restriction(
        _finite_gluing_presentations[presentation],
        _affine_backend.open_handle(larger),
        _affine_backend.open_handle(smaller),
    )
    return _rings_backend.reconstruct_oscar_morphism(
        cast(Any, larger).section_ring(),
        cast(Any, smaller).section_ring(),
        native,
    )


def finite_chart_preimage_equations(
    presentation: object,
    source_index: int,
    target_open: object,
) -> tuple[CategoryOfCategories.ElementType, ...]:
    """Normalize a cross-chart inverse image to principal root equations."""
    prepare_finite_gluing(presentation)
    chart = cast(Any, presentation).charts[source_index]
    native_open = oscar.covered_chart_open_preimage(
        _finite_gluing_presentations[presentation],
        _affine_backend.scheme_handle(chart),
        _affine_backend.open_handle(target_open),
    )
    return tuple(
        _rings_backend.reconstruct_oscar_element(chart.coordinate_ring(), equation)
        for equation in oscar.affine_open_complement_equations(native_open)
    )


def finite_overlap_restrictions(
    presentation: object,
    left_index: int,
    left_open: object,
    right_index: int,
    right_open: object,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    """Reconstruct the two restrictions to a pairwise overlap from OSCAR's structure sheaf."""
    prepare_finite_gluing(presentation)
    native_ring, native_left, native_right = oscar.covered_overlap_restrictions(
        _finite_gluing_presentations[presentation],
        _affine_backend.open_handle(left_open),
        _affine_backend.open_handle(right_open),
    )
    overlap_ring = _rings_backend.reconstruct_oscar_object(
        native_ring,
        (
            "covered-overlap",
            presentation,
            left_index,
            right_index,
            left_open,
            right_open,
        ),
    )
    return (
        _rings_backend.reconstruct_oscar_morphism(
            cast(Any, left_open).section_ring(), overlap_ring, native_left
        ),
        _rings_backend.reconstruct_oscar_morphism(
            cast(Any, right_open).section_ring(), overlap_ring, native_right
        ),
    )


def retain_covered_morphism(
    value: MorphismCategory.ObjectType,
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    chart_maps: tuple[MorphismCategory.ObjectType, ...],
) -> None:
    """Retain OSCAR's covered-scheme morphism for a compatible chart family."""
    native = oscar.covered_scheme_morphism_from_chart_maps(
        scheme_handle(source),
        scheme_handle(target),
        tuple(morphism_handle(mapping) for mapping in chart_maps),
    )
    _retain_morphism(value, native)


def _retain_morphism(value: MorphismCategory.ObjectType, native: OscarHandle) -> None:
    _morphisms.retain(value.base_category(), value, value.domain(), value.codomain(), native)


def morphism_handle(value: MorphismCategory.ObjectType) -> OscarHandle:
    if not _morphisms.has(value):
        word = value.word()
        if not word:
            native = oscar.covered_identity(scheme_handle(value.domain()))
        elif value.is_composite():
            first, second = value.factors()
            native = oscar.covered_compose(morphism_handle(second), morphism_handle(first))
        else:
            raise AssertionError(f"{value!r} has no retained OSCAR covered-scheme realization")
        _retain_morphism(value, native)
    native = _morphisms.realization(value).native
    assert isinstance(native, OscarHandle)
    return native


def native_scheme_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[OscarHandle]:
    morphism_handle(value)
    return _morphisms.realization(value)


def morphism_equal(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> bool | None:
    try:
        return oscar.covered_equal(morphism_handle(first), morphism_handle(second))
    except AssertionError:
        return None


def retain_chart_inclusion(
    arrow: MorphismCategory.ObjectType,
    affine: CategoryOfCategories.ElementType,
    glued: CategoryOfCategories.ElementType,
) -> None:
    native = oscar.covered_chart_inclusion(
        scheme_handle(arrow.domain()),
        _affine_backend.scheme_handle(affine),
        scheme_handle(glued),
    )
    _retain_morphism(arrow, native)


def retain_chart_map(
    arrow: MorphismCategory.ObjectType,
    source_affine: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    target_chart: CategoryOfCategories.ElementType,
    pullback: MorphismCategory.ObjectType,
) -> None:
    native_affine_map = oscar.affine_morphism_direct(
        _affine_backend.scheme_handle(source_affine),
        _affine_backend.scheme_handle(target_chart),
        _rings_backend.oscar_morphism_handle(pullback),
    )
    native = oscar.covered_chart_map(
        scheme_handle(arrow.domain()),
        _affine_backend.scheme_handle(source_affine),
        scheme_handle(target),
        native_affine_map,
    )
    _retain_morphism(arrow, native)
