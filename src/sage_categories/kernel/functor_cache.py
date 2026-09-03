"""Retain generic functor images by owned-value identity."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from sage_categories.kernel.sage_runtime import MonoDict, TripleDict

if TYPE_CHECKING:
    from sage_categories.kernel.roles import MorphismOfCategory, ObjectOfCategory

__all__: list[str] = []


class FunctorImageCache:
    """One functor's retained object and morphism images."""

    def __init__(self) -> None:
        self._objects: MonoDict = MonoDict()
        self._morphisms: TripleDict = TripleDict(weak_values=False)

    def object_image(
        self,
        source: ObjectOfCategory,
        construct: Callable[[ObjectOfCategory], ObjectOfCategory],
    ) -> ObjectOfCategory:
        if source not in self._objects:
            self._objects[source] = construct(source)
        return self._objects[source]

    def morphism_image(
        self,
        source: MorphismOfCategory,
        on_object: Callable[[ObjectOfCategory], ObjectOfCategory],
        construct: Callable[[MorphismOfCategory], MorphismOfCategory],
    ) -> MorphismOfCategory:
        key = (on_object(source.domain()), source, on_object(source.codomain()))
        if key not in self._morphisms:
            self._morphisms[key] = construct(source)
        return self._morphisms[key]
