"""Private OSCAR realization boundary for affine schemes and affine opens."""

from __future__ import annotations

from collections.abc import Callable
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

_objects: NativeObjectRealizations[OscarHandle, object] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[OscarHandle] = NativeMorphismRealizations()
_opens: dict[object, OscarHandle] = {}


def retain_spectrum(
    owner: Category,
    value: CategoryOfCategories.ElementType,
    coordinate_ring: CategoryOfCategories.ElementType,
    construction: object,
) -> None:
    native = oscar.affine_spec(_rings_backend.oscar_object_handle(coordinate_ring))
    assert oscar.same_native(oscar.affine_coordinate_ring(native), _rings_backend.oscar_object_handle(coordinate_ring))
    _objects.retain(owner, value, native, construction)


def native_affine_scheme(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[OscarHandle, object]:
    return _objects.realization(value)


def scheme_handle(value: CategoryOfCategories.ElementType) -> OscarHandle:
    native = native_affine_scheme(value).native
    assert isinstance(native, OscarHandle)
    return native


def _retain_morphism(value: MorphismCategory.ObjectType, native: OscarHandle) -> None:
    _morphisms.retain(value.base_category(), value, value.domain(), value.codomain(), native)


def morphism_handle(value: MorphismCategory.ObjectType) -> OscarHandle:
    if not _morphisms.has(value):
        pullback = value.pullback()
        native = oscar.affine_morphism(
            scheme_handle(value.domain()),
            scheme_handle(value.codomain()),
            _rings_backend.oscar_morphism_handle(pullback),
        )
        _retain_morphism(value, native)
    native = _morphisms.realization(value).native
    assert isinstance(native, OscarHandle)
    return native


def native_affine_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[OscarHandle]:
    morphism_handle(value)
    return _morphisms.realization(value)


def root_open(
    scheme: CategoryOfCategories.ElementType,
    make_open: Callable[[], CategoryOfCategories.ElementType],
) -> CategoryOfCategories.ElementType:
    value = make_open()
    _opens[value] = scheme_handle(scheme)
    return value


def principal_open(
    parent: CategoryOfCategories.ElementType,
    element: CategoryOfCategories.ElementType,
    make_open: Callable[[CategoryOfCategories.ElementType, MorphismCategory.ObjectType], CategoryOfCategories.ElementType],
) -> CategoryOfCategories.ElementType:
    native_open = oscar.principal_open(open_handle(parent), _rings_backend.oscar_element_handle(element))
    native_ring = oscar.affine_coordinate_ring(native_open)
    native_restriction = oscar.affine_pullback(oscar.principal_open_inclusion(native_open))
    section_ring, restriction = _rings_backend.principal_localization_from_native(
        element.parent(),
        element,
        native_ring,
        native_restriction,
    )
    value = make_open(section_ring, restriction)
    _opens[value] = native_open
    return value


def open_union(
    root: CategoryOfCategories.ElementType,
    pieces: tuple[CategoryOfCategories.ElementType, ...],
    construction: object,
    make_open: Callable[
        [
            CategoryOfCategories.ElementType,
            MorphismCategory.ObjectType,
            tuple[MorphismCategory.ObjectType, ...],
        ],
        CategoryOfCategories.ElementType,
    ],
) -> CategoryOfCategories.ElementType:
    """Retain a finite union of principal opens and its exact section restrictions."""
    native_pieces = tuple(open_handle(piece) for piece in pieces)
    native_open = oscar.affine_open_union(native_pieces)
    native_ring = oscar.affine_open_section_ring(native_open)
    section_ring = _rings_backend.reconstruct_oscar_object(native_ring, construction)
    root_restriction = _rings_backend.reconstruct_oscar_morphism(
        cast(Any, root).section_ring(),
        section_ring,
        oscar.affine_open_restriction(open_handle(root), native_open),
    )
    piece_restrictions = tuple(
        _rings_backend.reconstruct_oscar_morphism(
            section_ring,
            cast(Any, piece).section_ring(),
            oscar.affine_open_restriction(native_open, open_handle(piece)),
        )
        for piece in pieces
    )
    value = make_open(section_ring, root_restriction, piece_restrictions)
    _opens[value] = native_open
    return value


def open_contains(smaller: object, larger: object) -> bool:
    """Decide containment of two represented opens in one affine scheme."""
    return oscar.affine_open_contains(open_handle(smaller), open_handle(larger))


def open_restriction(
    smaller: object,
    larger: object,
) -> MorphismCategory.ObjectType:
    """Reconstruct ``OO(larger) -> OO(smaller)`` for an established containment."""
    native = oscar.affine_open_restriction(open_handle(larger), open_handle(smaller))
    return _rings_backend.reconstruct_oscar_morphism(
        cast(Any, larger).section_ring(),
        cast(Any, smaller).section_ring(),
        native,
    )


def open_intersection_equations(
    first: object,
    second: object,
) -> tuple[CategoryOfCategories.ElementType, ...]:
    """Return ambient-coordinate equations covering the represented intersection."""
    native = oscar.affine_open_intersection(open_handle(first), open_handle(second))
    ring = cast(Any, first).scheme().coordinate_ring()
    return tuple(
        _rings_backend.reconstruct_oscar_element(ring, equation)
        for equation in oscar.affine_open_complement_equations(native)
    )


def open_handle(value: CategoryOfCategories.ElementType) -> OscarHandle:
    assert value in _opens, f"{value!r} has no retained OSCAR affine-open realization"
    return _opens[value]
