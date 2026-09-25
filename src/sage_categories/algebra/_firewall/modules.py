"""Private Sage execution boundary for module ingestion."""

from __future__ import annotations

from collections.abc import Hashable

from sage.modules.free_module import FreeModule_generic
from sage.modules.free_module_element import FreeModuleElement
from sage.rings.integer import Integer
from sage.rings.integer_ring import ZZ

type Engine = FreeModule_generic[Integer]
type EngineElement = FreeModuleElement[Integer]


def require_integer_module(engine_module: Engine) -> Engine:
    """Return the native finite free module after checking the exact supported scalar base."""
    assert engine_module.base_ring() is ZZ, f"{engine_module!r} is not a module over Sage's integer ring"
    return engine_module


def module_member(engine_module: Engine, value: Hashable) -> bool:
    """Whether ``value`` is an element with exactly this native module as parent."""
    return isinstance(value, FreeModuleElement) and value.parent() is engine_module


def module_zero(engine_module: Engine) -> EngineElement:
    """The native additive zero of ``engine_module``."""
    return engine_module.zero_vector()


def module_add(engine_module: Engine, first: EngineElement, second: EngineElement) -> EngineElement:
    """Native addition after exact-parent validation."""
    assert module_member(engine_module, first) and module_member(engine_module, second)
    return first + second


def module_subtract(engine_module: Engine, minuend: EngineElement, subtrahend: EngineElement) -> EngineElement:
    """Native subtraction after exact-parent validation."""
    assert module_member(engine_module, minuend) and module_member(engine_module, subtrahend)
    return minuend - subtrahend


def integer_scale(engine_module: Engine, scalar: int, value: EngineElement) -> EngineElement:
    """The actual Sage ``ZZ`` scalar action on ``engine_module``."""
    assert module_member(engine_module, value)
    coefficient = ZZ(scalar)
    assert isinstance(coefficient, Integer)
    return coefficient * value


def module_rank(engine_module: Engine) -> int:
    """The finite rank of the exact native module."""
    return int(engine_module.rank())


def module_coordinates(engine_module: Engine, value: EngineElement) -> tuple[int, ...]:
    """Coordinates of one exact native module element in its supplied basis."""
    assert module_member(engine_module, value)
    coordinates: list[int] = []
    for coefficient in value.list():
        assert isinstance(coefficient, Integer)
        coordinates.append(int(coefficient))
    return tuple(coordinates)


def module_element(engine_module: Engine, coordinates: tuple[int, ...]) -> EngineElement:
    """The native element with the supplied exact basis coordinates."""
    assert len(coordinates) == module_rank(engine_module)
    return engine_module(coordinates)
