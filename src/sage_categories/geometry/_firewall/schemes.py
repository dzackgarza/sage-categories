"""Private OSCAR realization boundary for covered schemes."""

from __future__ import annotations

from sage_categories.algebra._firewall import commutative_rings as _rings_backend
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import NativeMorphismRealization, NativeMorphismRealizations, NativeObjectRealization, NativeObjectRealizations
from sage_categories.engines import oscar
from sage_categories.engines.julia_bridge import OscarHandle
from sage_categories.geometry._firewall import affine as _affine_backend


_objects: NativeObjectRealizations[OscarHandle, object] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[OscarHandle] = NativeMorphismRealizations()


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


def retain_gluing(
    owner: Category,
    value: CategoryOfCategories.ElementType,
    construction: object,
    left: CategoryOfCategories.ElementType,
    right: CategoryOfCategories.ElementType,
    left_open: CategoryOfCategories.ElementType,
    right_open: CategoryOfCategories.ElementType,
    left_to_right_pullback: MorphismCategory.ObjectType,
    right_to_left_pullback: MorphismCategory.ObjectType,
) -> None:
    native_left = _affine_backend.scheme_handle(left)
    native_right = _affine_backend.scheme_handle(right)
    left_to_right = oscar.affine_morphism_direct(
        _affine_backend.open_handle(left_open),
        _affine_backend.open_handle(right_open),
        _rings_backend.oscar_morphism_handle(left_to_right_pullback),
    )
    right_to_left = oscar.affine_morphism_direct(
        _affine_backend.open_handle(right_open),
        _affine_backend.open_handle(left_open),
        _rings_backend.oscar_morphism_handle(right_to_left_pullback),
    )
    gluing = oscar.simple_gluing(native_left, native_right, left_to_right, right_to_left)
    _retain_object(owner, value, oscar.glued_covered_scheme(native_left, native_right, gluing), construction)


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


def retain_gluing_mediator(
    arrow: MorphismCategory.ObjectType,
    glued: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    left: CategoryOfCategories.ElementType,
    right: CategoryOfCategories.ElementType,
    left_map: MorphismCategory.ObjectType,
    right_map: MorphismCategory.ObjectType,
) -> None:
    native = oscar.gluing_mediator(
        scheme_handle(glued),
        scheme_handle(target),
        _affine_backend.scheme_handle(left),
        _affine_backend.scheme_handle(right),
        morphism_handle(left_map),
        morphism_handle(right_map),
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


def structure_sheaf_restrictions(
    glued: CategoryOfCategories.ElementType,
    left_root: CategoryOfCategories.ElementType,
    right_root: CategoryOfCategories.ElementType,
    overlap: CategoryOfCategories.ElementType,
    left_ring: CategoryOfCategories.ElementType,
    right_ring: CategoryOfCategories.ElementType,
    overlap_ring: CategoryOfCategories.ElementType,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    native_sheaf = oscar.structure_sheaf(scheme_handle(glued))
    for open_set, ring in ((left_root, left_ring), (right_root, right_ring), (overlap, overlap_ring)):
        assert oscar.same_native(oscar.sheaf_value(native_sheaf, _affine_backend.open_handle(open_set)), _rings_backend.oscar_object_handle(ring))
    left = _rings_backend.reconstruct_oscar_morphism(
        left_ring,
        overlap_ring,
        oscar.sheaf_restriction(native_sheaf, _affine_backend.open_handle(left_root), _affine_backend.open_handle(overlap)),
    )
    right = _rings_backend.reconstruct_oscar_morphism(
        right_ring,
        overlap_ring,
        oscar.sheaf_restriction(native_sheaf, _affine_backend.open_handle(right_root), _affine_backend.open_handle(overlap)),
    )
    return left, right
