"""Cached slice constructions of a category."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from sage_categories.values import MathematicalObject

if TYPE_CHECKING:
    from sage_categories.category import Category


def cached_slice[SliceCategory: Category](
    category: Category,
    value: MathematicalObject,
    cache: dict[int, SliceCategory],
    constructor: Callable[[Category, MathematicalObject], SliceCategory],
) -> SliceCategory:
    """Return the canonical slice construction for ``value``."""
    key = id(value)
    result = cache.get(key)
    if result is None:
        result = constructor(category, value)
        cache[key] = result
    return result
