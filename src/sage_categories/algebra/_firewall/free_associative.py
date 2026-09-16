"""Private native execution for free associative algebras."""

from __future__ import annotations

from collections.abc import Mapping

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.native import NativeObjectRealizations
from sage_categories.engines import free_algebras


_objects: NativeObjectRealizations[object, object] = NativeObjectRealizations()
_pending: dict[object, object] = {}


def prepare(construction: object, names: tuple[str, ...]) -> None:
    """Allocate the native algebra for one owned construction before its monoid is assembled."""
    _pending[construction] = free_algebras.integer_free_algebra(names)


def multiply(
    construction: object,
    left: Mapping[tuple[int, ...], int],
    right: Mapping[tuple[int, ...], int],
) -> dict[tuple[int, ...], int]:
    return free_algebras.multiply(_pending[construction], left, right)


def retain(owner: Category, value: CategoryOfCategories.ElementType, construction: object) -> None:
    native = _pending.pop(construction)
    _objects.retain(owner, value, native, construction)


def construction(value: CategoryOfCategories.ElementType) -> object:
    return _objects.realization(value).construction


def owner(value: CategoryOfCategories.ElementType) -> Category:
    return _objects.realization(value).owner


def generator(value: CategoryOfCategories.ElementType, position: int) -> dict[tuple[int, ...], int]:
    return free_algebras.generator(_objects.realization(value).native, position)


def substitute(
    value: CategoryOfCategories.ElementType,
    terms: Mapping[tuple[int, ...], int],
    image_terms: tuple[Mapping[tuple[int, ...], int], ...],
) -> dict[tuple[int, ...], int]:
    return free_algebras.substitute(_objects.realization(value).native, terms, image_terms)
