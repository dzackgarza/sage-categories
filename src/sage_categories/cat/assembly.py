"""Cat-owned retention for local mathematical constructors.

Leaves call this surface in terms of *chosen values*: points with a datum, a chosen
construction for exact inputs, or a selected value such as an enumeration.  Identity
keys and storage remain implementation details here rather than leaking into theory.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import Any

from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

__all__ = ["chosen_construction", "has_selected_value", "point_from_datum", "select_value", "selected_value"]


@cached_function
def point_from_datum(parent: Any, datum: Hashable) -> Any:
    """Return the one retained local point of ``parent`` carrying ``datum``."""
    return parent.ObjectType(datum)


_chosen: dict[tuple[int, str], dict[tuple[tuple[int, object], ...], object]] = {}
_selected: dict[tuple[int, str], dict[tuple[tuple[int, object], ...], object]] = {}


def chosen_construction[Value](
    owner: object,
    family: str,
    parameters: tuple[object, ...],
    construct: Callable[[], Value],
) -> Value:
    """Return the chosen value of one named construction on exact retained inputs."""
    store = _chosen.setdefault((id(owner), family), {})
    key = identity_key(*parameters)
    if key not in store:
        store[key] = construct()
    return store[key]  # type: ignore[return-value]


def select_value(owner: object, family: str, parameters: tuple[object, ...], value: object) -> None:
    """Select ``value`` for a named mathematical choice on exact retained inputs."""
    _selected.setdefault((id(owner), family), {})[identity_key(*parameters)] = value


def has_selected_value(owner: object, family: str, parameters: tuple[object, ...]) -> bool:
    """Whether a named mathematical choice has already been selected."""
    return identity_key(*parameters) in _selected.get((id(owner), family), {})


def selected_value[Value](owner: object, family: str, parameters: tuple[object, ...]) -> Value:
    """Read a value previously selected for one named mathematical choice."""
    key = identity_key(*parameters)
    store = _selected.get((id(owner), family), {})
    assert key in store, f"{family!r} has no selected value for {parameters!r}"
    return store[key]  # type: ignore[return-value]
