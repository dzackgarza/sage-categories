"""Private Sage execution boundary for module ingestion."""

from __future__ import annotations

from collections.abc import Hashable

from sage.modules.free_module import Module_free_ambient
from sage.rings.integer_ring import ZZ
from sage.structure.element import Element as SageElement


def require_integer_module(engine_module: object) -> Module_free_ambient:
    """Return the native finite free module after checking the exact supported scalar base."""
    assert isinstance(engine_module, Module_free_ambient), f"{engine_module!r} is not a Sage finite free module"
    assert engine_module.base_ring() is ZZ, f"{engine_module!r} is not a module over Sage's integer ring"
    return engine_module


def module_member(engine_module: Module_free_ambient, value: object) -> bool:
    """Whether ``value`` is an element with exactly this native module as parent."""
    return isinstance(value, SageElement) and value.parent() is engine_module


def module_zero(engine_module: Module_free_ambient) -> Hashable:
    """The native additive zero of ``engine_module``."""
    return engine_module.zero()


def module_add(engine_module: Module_free_ambient, first: object, second: object) -> Hashable:
    """Native addition after exact-parent validation."""
    assert module_member(engine_module, first) and module_member(engine_module, second)
    return first + second


def module_subtract(engine_module: Module_free_ambient, minuend: object, subtrahend: object) -> Hashable:
    """Native subtraction after exact-parent validation."""
    assert module_member(engine_module, minuend) and module_member(engine_module, subtrahend)
    return minuend - subtrahend


def integer_scale(engine_module: Module_free_ambient, scalar: object, value: object) -> Hashable:
    """The actual Sage ``ZZ`` scalar action on ``engine_module``."""
    assert module_member(engine_module, value)
    return ZZ(scalar) * value


def module_rank(engine_module: Module_free_ambient) -> int:
    """The finite rank of the exact native module."""
    return int(engine_module.rank())


def module_coordinates(engine_module: Module_free_ambient, value: object) -> tuple[int, ...]:
    """Coordinates of one exact native module element in its supplied basis."""
    assert module_member(engine_module, value)
    return tuple(int(coefficient) for coefficient in value)


def module_element(engine_module: Module_free_ambient, coordinates: tuple[int, ...]) -> Hashable:
    """The native element with the supplied exact basis coordinates."""
    assert len(coordinates) == module_rank(engine_module)
    return engine_module(coordinates)
