from collections.abc import Callable
from typing import Any

def compatible_families(
    vertices: tuple[Any, ...],
    arrows: tuple[Any, ...],
    families: tuple[tuple[Any, ...], ...],
    image: Callable[[Any, Any], Any],
) -> tuple[tuple[Any, ...], ...]: ...
