"""Lazy ring-category access shared by geometry modules."""

from importlib import import_module
from typing import Any

from sage_categories.cat.declarations import Sets


def rings() -> Any:
    """The owned category of ring objects in sets, loaded only after geometry imports settle."""
    return import_module("sage_categories.cat.structured_objects").Rings(Sets)


def commutative_rings() -> Any:
    """The owned full subcategory of commutative ring objects in sets."""
    return rings().Commutative()
