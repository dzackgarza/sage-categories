"""Shared loader for the repository's pinned Julia bridge."""

from __future__ import annotations

from functools import cache
from importlib import import_module
from pathlib import Path
from typing import Any

__all__ = ["catlab_bridge", "oscar_bridge"]


def _bridge_source(name: str) -> Path:
    return Path(__file__).with_name(name)


@cache
def _main() -> Any:
    juliacall = import_module("juliacall")
    return juliacall.Main


@cache
def catlab_bridge() -> Any:
    """Load the pinned Catlab/GATlab bridge through JuliaCall exactly once."""
    main = _main()
    main.include(str(_bridge_source("SageCategoriesBridge.jl")))
    return main.SageCategoriesBridge


@cache
def oscar_bridge() -> Any:
    """Load the pinned OSCAR bridge lazily, without making Catlab startup import OSCAR."""
    main = _main()
    main.include(str(_bridge_source("OscarBridge.jl")))
    return main.SageCategoriesOscarBridge
