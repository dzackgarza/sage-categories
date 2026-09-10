"""ModulePresentationsForCAP execution for finitely presented abelian groups.

The public object remains the owned object of ``Ab``.  CAP receives only the
selected integer presentation and morphism matrices, computes the categorical
construction, and its native objects/morphisms are retained privately for
subsequent engine operations.  Reconstruction of the public carrier uses
Sage's mature finitely-presented-module engine on CAP's returned relation
matrix; no CAP object escapes this module.
"""

from __future__ import annotations

from functools import cache

from sage.libs.gap.element import GapElement
from sage.libs.gap.libgap import libgap
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

__all__ = ["coequalizer_projection"]


@cache
def _ring() -> GapElement:
    load_packages(PRESENTED_MODULE_PACKAGES)
    return libgap.HOMALG_MATRICES.ZZ


@cache
def _category() -> GapElement:
    return libgap.LeftPresentations(_ring())


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
    from sage_categories.algebra.abelian import presentation

    form = presentation(value)
    rank = form.rank()
    relations = []
    for position, order in enumerate(form.orders):
        if not order:
            continue
        row = [0] * rank
        row[position] = int(order)
        relations.append(tuple(row))
    native = libgap.AsLeftPresentation(
        _category(),
        _homalg_matrix(tuple(relations), rank),
    )
    retain_presented_native_object(value, native, form.orders)
    return native


def _native_morphism(value: object) -> GapElement:
    if _has_native_morphism(value):
        return presented_native_morphism(value).native
    from sage_categories.algebra.abelian import linear_form

    form = linear_form(value)
    rows = tuple(tuple(int(entry) for entry in row) for row in form.matrix.rows())
    native = libgap.PresentationMorphism(
        _native_object(value.domain()),
        _homalg_matrix(rows, form.target.rank()),
        _native_object(value.codomain()),
    )
    retain_presented_native_morphism(value, native)
    return native


def _integer_matrix_rows(native_matrix: GapElement) -> tuple[tuple[int, ...], ...]:
    row_count = int(libgap.NumberRows(native_matrix))
    column_count = int(libgap.NumberColumns(native_matrix))
    entries = tuple(
        int(str(entry)) for entry in libgap.EntriesOfHomalgMatrix(native_matrix)
    )
    assert len(entries) == row_count * column_count
    return tuple(
        tuple(
            entries[row * column_count + column]
            for column in range(column_count)
        )
        for row in range(row_count)
    )


def _integer_rows(native_object: GapElement) -> tuple[tuple[int, ...], ...]:
    return _integer_matrix_rows(libgap.UnderlyingMatrix(native_object))


def _public_engine_from_native(native_object: GapElement):
    relation_matrix = libgap.UnderlyingMatrix(native_object)
    rank = int(libgap.NumberColumns(relation_matrix))
    free = FreeModule(ZZ, rank)
    rows = _integer_rows(native_object)
    relations = tuple(free(vector(ZZ, row)) for row in rows)
    return free, free / free.span(relations)


def coequalizer_projection(first: object, second: object):
    """Return CAP's selected cokernel of ``first-second`` as an owned ``Ab`` map."""
    from sage_categories.algebra.abelian import (
        LinearForm,
        _group_from_engine,
        _linear_homomorphism,
        _matrix_of_rows,
        linear_form,
        presentation,
    )

    source, target = first.domain(), first.codomain()
    assert second.domain() is source and second.codomain() is target
    first_form, second_form = linear_form(first), linear_form(second)
    difference = first_form.matrix - second_form.matrix
    rows = tuple(tuple(int(entry) for entry in row) for row in difference.rows())
    native_difference = libgap.PresentationMorphism(
        _native_object(source),
        _homalg_matrix(rows, first_form.target.rank()),
        _native_object(target),
    )
    native_projection = libgap.CokernelProjection(native_difference)
    native_apex = libgap.Range(native_projection)

    free, engine = _public_engine_from_native(native_apex)
    apex = _group_from_engine(engine)
    retain_presented_native_object(apex, native_apex, _integer_rows(native_apex))

    apex_form = presentation(apex)
    target_form = presentation(target)
    native_projection_rows = _integer_matrix_rows(
        libgap.UnderlyingMatrix(native_projection)
    )
    assert len(native_projection_rows) == target_form.rank()
    projection_rows = tuple(
        vector(
            ZZ,
            apex_form.coordinates(
                engine(free(vector(ZZ, native_projection_rows[position])))
            ),
        )
        for position in range(target_form.rank())
    )
    owned_projection = _linear_homomorphism(
        target,
        apex,
        LinearForm(
            target_form,
            apex_form,
            _matrix_of_rows(projection_rows, apex_form.rank()),
        ),
    )
    retain_presented_native_morphism(owned_projection, native_projection)
    return owned_projection, free, engine
