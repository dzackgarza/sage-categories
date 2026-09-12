"""ModulePresentationsForCAP execution for finitely presented abelian groups.

The public object remains the owned object of ``Ab``.  CAP receives only the
selected integer presentation and morphism matrices, computes the categorical
construction, and its native objects/morphisms are retained privately for
subsequent engine operations.  Reconstruction of the public carrier uses
Sage's mature finitely-presented-module engine on CAP's returned relation
matrix; no CAP object escapes this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from sage.libs.gap.element import GapElement
from sage.libs.gap.libgap import libgap
from sage.matrix.constructor import matrix
from sage.modules.free_module import FreeModule
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ

from sage_categories.algebra._presented_modules_cap import (
    presented_native_morphism,
    presented_native_object,
    retain_presented_native_morphism,
    retain_presented_native_object,
)
from sage_categories.engines.gap import PRESENTED_MODULE_PACKAGES, load_packages

__all__ = [
    "coequalizer_mediator",
    "coequalizer_projection",
    "colift_along_epimorphism",
    "direct_sum_coproduct_lift",
    "direct_sum_product_lift",
    "retain_binary_biproduct",
    "tensor_associator",
    "tensor_element",
    "tensor_left_unitor",
    "tensor_mediator",
    "tensor_morphism",
    "tensor_object",
    "tensor_right_unitor",
    "zero_morphism",
]


@dataclass(frozen=True, eq=False, slots=True)
class _PresentationBridge:
    """The raw CAP presentation basis behind one reconstructed public Smith basis."""

    free: object
    engine: object


@dataclass(frozen=True, eq=False, slots=True)
class _DirectSumBridge:
    """A raw CAP direct-sum basis assembled from the retained factor bases."""

    factors: tuple[object, ...]


_cokernel_differences: dict[int, tuple[object, GapElement]] = {}


@cache
def _ring() -> GapElement:
    load_packages(PRESENTED_MODULE_PACKAGES)
    return libgap.HomalgRingOfIntegers()


@cache
def _category() -> GapElement:
    ring = _ring()
    return libgap.LeftPresentations(ring)


def _homalg_matrix(rows: tuple[tuple[int, ...], ...], columns: int) -> GapElement:
    ring = _ring()
    if not rows:
        return libgap.HomalgZeroMatrix(0, columns, ring)
    assert all(len(row) == columns for row in rows)
    return libgap.HomalgMatrix(
        [list(map(int, row)) for row in rows],
        len(rows),
        columns,
        ring,
    )


def _has_native_object(value: object) -> bool:
    try:
        presented_native_object(value)
    except AssertionError:
        return False
    return True


def _has_native_morphism(value: object) -> bool:
    try:
        presented_native_morphism(value)
    except AssertionError:
        return False
    return True


def _native_object(value: object) -> GapElement:
    if _has_native_object(value):
        return presented_native_object(value).native
    from sage_categories.algebra.abelian import _coordinates

    category = _category()
    form = _coordinates(value)
    rank = form.rank()
    relations = []
    for position, order in enumerate(form.orders):
        if not order:
            continue
        row = [0] * rank
        row[position] = int(order)
        relations.append(tuple(row))
    native = libgap.AsLeftPresentation(
        category,
        _homalg_matrix(tuple(relations), rank),
    )
    retain_presented_native_object(value, native, None)
    return native


def _bridge(value: object) -> _PresentationBridge | _DirectSumBridge | None:
    data = presented_native_object(value).construction.data
    assert data is None or isinstance(data, (_PresentationBridge, _DirectSumBridge))
    return data


def _public_coordinates_from_raw(value: object, raw_coordinates) -> tuple[int, ...]:
    from sage_categories.algebra.abelian import _coordinates

    form = _coordinates(value)
    bridge = _bridge(value)
    if bridge is None:
        return form.coordinates(form.element(tuple(int(entry) for entry in raw_coordinates)))
    if isinstance(bridge, _PresentationBridge):
        raw = bridge.free(vector(ZZ, raw_coordinates))
        return form.coordinates(bridge.engine(raw))
    result = []
    start = 0
    for factor in bridge.factors:
        native = _native_object(factor)
        size = int(libgap.NumberColumns(libgap.UnderlyingMatrix(native)))
        result.extend(
            _public_coordinates_from_raw(
                factor,
                raw_coordinates[start : start + size],
            )
        )
        start += size
    assert start == len(raw_coordinates)
    return tuple(result)


def _raw_coordinates_from_public(value: object, public_coordinates) -> tuple[int, ...]:
    from sage_categories.algebra.abelian import _coordinates

    form = _coordinates(value)
    normalized = form.element(tuple(int(entry) for entry in public_coordinates))
    bridge = _bridge(value)
    if bridge is None:
        return tuple(int(entry) for entry in form.coordinates(normalized))
    if isinstance(bridge, _PresentationBridge):
        element = bridge.engine(normalized)
        return tuple(int(entry) for entry in element.lift())
    normalized_coordinates = form.coordinates(normalized)
    result = []
    start = 0
    for factor in bridge.factors:
        factor_rank = _coordinates(factor).rank()
        result.extend(
            _raw_coordinates_from_public(
                factor,
                normalized_coordinates[start : start + factor_rank],
            )
        )
        start += factor_rank
    assert start == len(normalized_coordinates)
    return tuple(result)


def _native_matrix_from_public(value: object) -> GapElement:
    from sage_categories.algebra.abelian import _coordinates

    source, target = value.domain(), value.codomain()
    source_form = _coordinates(source)
    target_form = _coordinates(target)
    native_source = _native_object(source)
    native_target = _native_object(target)
    source_rank = int(libgap.NumberColumns(libgap.UnderlyingMatrix(native_source)))
    target_rank = int(libgap.NumberColumns(libgap.UnderlyingMatrix(native_target)))
    rows = []
    for position in range(source_rank):
        raw_source = [0] * source_rank
        raw_source[position] = 1
        public_source = source_form.element(_public_coordinates_from_raw(source, raw_source))
        public_target = target_form.coordinates(value(source.point(public_source)).datum())
        rows.append(_raw_coordinates_from_public(target, public_target))
    return _homalg_matrix(tuple(rows), target_rank)


def _native_morphism(value: object) -> GapElement:
    if _has_native_morphism(value):
        return presented_native_morphism(value).native
    native = libgap.PresentationMorphism(
        _native_object(value.domain()),
        _native_matrix_from_public(value),
        _native_object(value.codomain()),
    )
    assert bool(libgap.IsWellDefined(native)), f"CAP rejected the public morphism {value!r}"
    retain_presented_native_morphism(value, native)
    return native


def _integer_matrix_rows(native_matrix: GapElement) -> tuple[tuple[int, ...], ...]:
    row_count = int(libgap.NumberRows(native_matrix))
    column_count = int(libgap.NumberColumns(native_matrix))
    entries = tuple(int(str(entry)) for entry in libgap.EntriesOfHomalgMatrix(native_matrix))
    assert len(entries) == row_count * column_count
    return tuple(tuple(entries[row * column_count + column] for column in range(column_count)) for row in range(row_count))


def _integer_rows(native_object: GapElement) -> tuple[tuple[int, ...], ...]:
    return _integer_matrix_rows(libgap.UnderlyingMatrix(native_object))


def _public_engine_from_native(native_object: GapElement):
    relation_matrix = libgap.UnderlyingMatrix(native_object)
    rank = int(libgap.NumberColumns(relation_matrix))
    free = FreeModule(ZZ, rank)
    rows = _integer_rows(native_object)
    relations = tuple(free(vector(ZZ, row)) for row in rows)
    return free, free / free.span(relations)


def _owned_morphism_from_native(source: object, target: object, native: GapElement):
    from sage_categories.algebra.abelian import (
        AbelianGroups,
        _rule_abelian_homomorphism,
        _coordinates,
    )
    from sage_categories.cat.morphisms import Mor
    from sage_categories.kernel.refinement import refine

    source_form = _coordinates(source)
    target_form = _coordinates(target)
    native_matrix = matrix(ZZ, _integer_matrix_rows(libgap.UnderlyingMatrix(native)))

    def evaluate(datum):
        public_source = source_form.coordinates(datum)
        raw_source = _raw_coordinates_from_public(source, public_source)
        raw_target = vector(ZZ, raw_source) * native_matrix
        public_target = _public_coordinates_from_raw(target, raw_target)
        return target_form.element(public_target)

    owned = _rule_abelian_homomorphism(source, target, evaluate)
    refine(owned, Mor(AbelianGroups())(source, target))
    retain_presented_native_morphism(owned, native)
    return owned


def homomorphism_from_rule(source: object, target: object, rule):
    """Construct the presented-module morphism determined by generator images.

    Public data are converted only at the boundary.  CAP owns the relation check through
    ``IsWellDefined`` and the returned native presentation morphism remains the computational
    authority for the public arrow.
    """
    from sage_categories.algebra.abelian import _coordinates

    source_form = _coordinates(source)
    target_form = _coordinates(target)
    source_native = _native_object(source)
    target_native = _native_object(target)
    source_rank = int(libgap.NumberColumns(libgap.UnderlyingMatrix(source_native)))
    target_rank = int(libgap.NumberColumns(libgap.UnderlyingMatrix(target_native)))
    rows = []
    for position in range(source_rank):
        raw_source = [0] * source_rank
        raw_source[position] = 1
        public_source = source_form.element(_public_coordinates_from_raw(source, raw_source))
        public_target = target_form.coordinates(rule(public_source))
        rows.append(_raw_coordinates_from_public(target, public_target))
    native = libgap.PresentationMorphism(
        source_native,
        _homalg_matrix(tuple(rows), target_rank),
        target_native,
    )
    assert bool(libgap.IsWellDefined(native)), "CAP rejected the supplied generator images"
    return _owned_morphism_from_native(source, target, native)


def coequalizer_projection(first: object, second: object):
    """Return CAP's selected cokernel of ``first-second`` as an owned ``Ab`` map."""
    from sage_categories.algebra.abelian import _group_from_engine

    source, target = first.domain(), first.codomain()
    assert second.domain() is source and second.codomain() is target
    native_difference = libgap.SubtractionForMorphisms(
        _native_morphism(first),
        _native_morphism(second),
    )
    native_projection = libgap.CokernelProjection(native_difference)
    native_apex = libgap.Range(native_projection)

    free, engine = _public_engine_from_native(native_apex)
    apex = _group_from_engine(engine)
    retain_presented_native_object(
        apex,
        native_apex,
        _PresentationBridge(free, engine),
    )
    owned_projection = _owned_morphism_from_native(target, apex, native_projection)
    _cokernel_differences[id(owned_projection)] = (
        owned_projection,
        native_difference,
    )
    return owned_projection


def coequalizer_mediator(projection: object, coequalizing: object):
    """Return CAP's universal colift through an already retained cokernel projection."""
    record = _cokernel_differences.get(id(projection))
    assert record is not None and record[0] is projection, f"{projection!r} is not a retained CAP cokernel projection"
    native_difference = record[1]
    apex = projection.codomain()
    target = coequalizing.codomain()
    assert coequalizing.domain() is projection.domain()
    native = libgap.CokernelColiftWithGivenCokernelObject(
        native_difference,
        _native_object(target),
        _native_morphism(coequalizing),
        _native_object(apex),
    )
    return _owned_morphism_from_native(apex, target, native)


def colift_along_epimorphism(epimorphism: object, morphism: object):
    """Return CAP's colift of ``morphism`` through the selected epimorphism.

    Both public arrows have one source.  CAP computes the unique descended
    arrow on the codomain of ``epimorphism`` when the latter is an
    epimorphism and ``morphism`` kills its kernel; only the reconstructed
    owned arrow crosses back into the public layer.
    """
    assert morphism.domain() is epimorphism.domain()
    native = libgap.ColiftAlongEpimorphism(
        _native_morphism(epimorphism),
        _native_morphism(morphism),
    )
    return _owned_morphism_from_native(
        epimorphism.codomain(),
        morphism.codomain(),
        native,
    )


def retain_binary_biproduct(first: object, second: object, apex: object):
    """Retain CAP's direct sum on the already selected owned biproduct apex."""
    factors = (first, second)
    native_factors = [_native_object(factor) for factor in factors]
    category = _category()
    native_apex = libgap.DirectSumOp(category, native_factors)
    retain_presented_native_object(apex, native_apex, _DirectSumBridge(factors))
    projections = tuple(
        _owned_morphism_from_native(
            apex,
            factor,
            libgap.ProjectionInFactorOfDirectSumWithGivenDirectSum(
                category,
                native_factors,
                index + 1,
                native_apex,
            ),
        )
        for index, factor in enumerate(factors)
    )
    injections = tuple(
        _owned_morphism_from_native(
            factor,
            apex,
            libgap.InjectionOfCofactorOfDirectSumWithGivenDirectSum(
                category,
                native_factors,
                index + 1,
                native_apex,
            ),
        )
        for index, factor in enumerate(factors)
    )
    return projections, injections


def direct_sum_product_lift(
    factors: tuple[object, ...],
    apex: object,
    source: object,
    components: tuple[object, ...],
):
    """Return CAP's universal map from ``source`` into the retained direct sum."""
    native_factors = [_native_object(factor) for factor in factors]
    native = libgap.UniversalMorphismIntoDirectSumWithGivenDirectSum(
        _category(),
        native_factors,
        _native_object(source),
        [_native_morphism(component) for component in components],
        _native_object(apex),
    )
    return _owned_morphism_from_native(source, apex, native)


def direct_sum_coproduct_lift(
    factors: tuple[object, ...],
    apex: object,
    target: object,
    components: tuple[object, ...],
):
    """Return CAP's universal map from the retained direct sum into ``target``."""
    native_factors = [_native_object(factor) for factor in factors]
    native = libgap.UniversalMorphismFromDirectSumWithGivenDirectSum(
        _category(),
        native_factors,
        _native_object(target),
        [_native_morphism(component) for component in components],
        _native_object(apex),
    )
    return _owned_morphism_from_native(apex, target, native)


def zero_morphism(source: object, target: object):
    """Return CAP's additive zero morphism on the retained public endpoints."""
    native = libgap.ZeroMorphism(
        _native_object(source),
        _native_object(target),
    )
    return _owned_morphism_from_native(source, target, native)


def tensor_object(first: object, second: object):
    """Return CAP's selected tensor product as the same public owned ``Ab`` object."""
    from sage_categories.algebra.abelian import _group_from_engine

    native = libgap.TensorProductOnObjects(
        _native_object(first),
        _native_object(second),
    )
    free, engine = _public_engine_from_native(native)
    result = _group_from_engine(engine)
    retain_presented_native_object(result, native, _PresentationBridge(free, engine))
    return result, engine


def tensor_element(first: object, second: object, tensor: object, left: object, right: object):
    """Return the public tensor datum of two public factor data via CAP's raw basis."""
    from sage_categories.algebra.abelian import _coordinates

    first_form = _coordinates(first)
    second_form = _coordinates(second)
    left_raw = _raw_coordinates_from_public(first, first_form.coordinates(left))
    right_raw = _raw_coordinates_from_public(second, second_form.coordinates(right))
    raw_pair = tuple(left_coefficient * right_coefficient for left_coefficient in left_raw for right_coefficient in right_raw)
    bridge = _bridge(tensor)
    assert isinstance(bridge, _PresentationBridge)
    return bridge.engine(bridge.free(vector(ZZ, raw_pair)))


def tensor_mediator(
    first: object,
    second: object,
    tensor: object,
    target: object,
    biadditive,
):
    """Return the CAP morphism induced by one public biadditive rule on factor data."""
    from sage_categories.algebra.abelian import _coordinates

    first_native = _native_object(first)
    second_native = _native_object(second)
    first_raw_rank = int(libgap.NumberColumns(libgap.UnderlyingMatrix(first_native)))
    second_raw_rank = int(libgap.NumberColumns(libgap.UnderlyingMatrix(second_native)))
    target_native = _native_object(target)
    target_raw_rank = int(libgap.NumberColumns(libgap.UnderlyingMatrix(target_native)))
    first_form = _coordinates(first)
    second_form = _coordinates(second)
    target_form = _coordinates(target)
    rows = []
    for first_position in range(first_raw_rank):
        first_raw = [0] * first_raw_rank
        first_raw[first_position] = 1
        first_public = first_form.element(_public_coordinates_from_raw(first, first_raw))
        for second_position in range(second_raw_rank):
            second_raw = [0] * second_raw_rank
            second_raw[second_position] = 1
            second_public = second_form.element(_public_coordinates_from_raw(second, second_raw))
            image = biadditive(first_public, second_public)
            public_target = target_form.coordinates(image)
            rows.append(_raw_coordinates_from_public(target, public_target))
    native = libgap.PresentationMorphism(
        _native_object(tensor),
        _homalg_matrix(tuple(rows), target_raw_rank),
        target_native,
    )
    return _owned_morphism_from_native(tensor, target, native)


def tensor_morphism(
    first: object,
    second: object,
    source_tensor: object,
    target_tensor: object,
):
    """Return CAP's ``first tensor second`` on the retained public tensor objects."""
    native_source = presented_native_object(source_tensor).native
    native_target = presented_native_object(target_tensor).native
    native = libgap.TensorProductOnMorphismsWithGivenTensorProducts(
        native_source,
        _native_morphism(first),
        _native_morphism(second),
        native_target,
    )
    return _owned_morphism_from_native(source_tensor, target_tensor, native)


def tensor_associator(
    first: object,
    second: object,
    third: object,
    source_tensor: object,
    target_tensor: object,
    *,
    left_to_right: bool,
):
    """Return CAP's associator between the already selected public tensor objects."""
    operation = libgap.AssociatorLeftToRightWithGivenTensorProducts if left_to_right else libgap.AssociatorRightToLeftWithGivenTensorProducts
    native = operation(
        _native_object(source_tensor),
        _native_object(first),
        _native_object(second),
        _native_object(third),
        _native_object(target_tensor),
    )
    return _owned_morphism_from_native(source_tensor, target_tensor, native)


def tensor_left_unitor(group: object, tensor: object, *, inverse: bool):
    """Return CAP's left unitor, or its inverse, for the selected tensor object."""
    native = (
        libgap.LeftUnitorInverseWithGivenTensorProduct(
            _native_object(group),
            _native_object(tensor),
        )
        if inverse
        else libgap.LeftUnitorWithGivenTensorProduct(
            _native_object(group),
            _native_object(tensor),
        )
    )
    source, target = (group, tensor) if inverse else (tensor, group)
    return _owned_morphism_from_native(source, target, native)


def tensor_right_unitor(group: object, tensor: object, *, inverse: bool):
    """Return CAP's right unitor, or its inverse, for the selected tensor object."""
    native = (
        libgap.RightUnitorInverseWithGivenTensorProduct(
            _native_object(group),
            _native_object(tensor),
        )
        if inverse
        else libgap.RightUnitorWithGivenTensorProduct(
            _native_object(group),
            _native_object(tensor),
        )
    )
    source, target = (group, tensor) if inverse else (tensor, group)
    return _owned_morphism_from_native(source, target, native)
