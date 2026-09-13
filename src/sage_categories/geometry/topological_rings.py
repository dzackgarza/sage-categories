"""Topological rings with one retained underlying set for algebra and topology."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import ask
from sage_categories.geometry._ring_categories import rings as _rings
from sage_categories.geometry.spaces import (
    TopologicalSpacesCategory,
    _topological_space_projection,
)
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method

__all__ = [
    "BinaryContinuity",
    "ProductTopologyOpen",
    "TopologicalRings",
    "TopologicalRingsCategory",
]

@dataclass(frozen=True, eq=False, slots=True)
class ProductTopologyOpen:
    """A represented open in the binary product topology of one space with itself."""

    space: TopologicalSpacesCategory.ObjectType
    membership: Callable[[tuple[object, object]], bool | None]
    construction: object

    def contains(self, first: object, second: object) -> bool | None:
        return self.membership((first, second))


@dataclass(frozen=True, eq=False, slots=True)
class BinaryContinuity:
    """Continuity data for a binary operation on one represented topological space."""

    space: TopologicalSpacesCategory.ObjectType
    operation: MorphismCategory.ObjectType
    preimage_rule: Callable[[CategoryOfCategories.ElementType], ProductTopologyOpen]

    def preimage(
        self,
        open_object: CategoryOfCategories.ElementType,
    ) -> ProductTopologyOpen:
        assert open_object in self.space.open_category()
        result = self.preimage_rule(open_object)
        assert result.space is self.space
        return result


@dataclass(frozen=True, eq=False, slots=True)
class _TopologicalRingData:
    ring: CategoryOfCategories.ElementType
    space: TopologicalSpacesCategory.ObjectType
    addition: BinaryContinuity
    multiplication: BinaryContinuity


class TopologicalRingsCategory(Category[[MorphismCategory.ObjectType], []]):
    """Ring objects in ``Sets`` equipped with a topology on the exact same carrier."""

    class ObjectType:
        def __init__(self, data: _TopologicalRingData) -> None:
            self._ring, self._space = data.ring, data.space
            self._addition, self._multiplication = data.addition, data.multiplication

        def ring(self) -> CategoryOfCategories.ElementType:
            return self._ring

        def space(self) -> TopologicalSpacesCategory.ObjectType:
            return self._space

        def addition_continuity(self) -> BinaryContinuity:
            return self._addition

        def multiplication_continuity(self) -> BinaryContinuity:
            return self._multiplication

        def addition_preimage(
            self,
            open_object: CategoryOfCategories.ElementType,
        ) -> ProductTopologyOpen:
            return self._addition.preimage(open_object)

        def multiplication_preimage(
            self,
            open_object: CategoryOfCategories.ElementType,
        ) -> ProductTopologyOpen:
            return self._multiplication.preimage(open_object)

    class ElementType:
        pass

    class MorphismType:
        def __init__(
            self,
            data: tuple[MorphismCategory.ObjectType, TopologicalSpacesCategory.MorphismType],
        ) -> None:
            self._ring_map, self._continuous_map = data

        def ring_map(self) -> MorphismCategory.ObjectType:
            return self._ring_map

        def continuous_map(self) -> TopologicalSpacesCategory.MorphismType:
            return self._continuous_map

    @cached_method
    def to_rings(self) -> Functor:
        return Fun(self, _rings())(
            lambda value: cast(Any, value).ring(),
            lambda arrow: cast(Any, arrow).ring_map(),
        )

    @cached_method
    def to_spaces(self) -> Functor:
        return _topological_space_projection(self)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.to_rings(), self.to_spaces())

    def __call__(
        self,
        ring: CategoryOfCategories.ElementType,
        space: TopologicalSpacesCategory.ObjectType,
        addition: BinaryContinuity,
        multiplication: BinaryContinuity,
    ) -> TopologicalRingsCategory.ObjectType:
        rings = _rings()
        assert ring in rings
        assert rings.forgetful().on_object(ring) is space.carrier()
        assert addition.space is space and multiplication.space is space
        assert addition.operation is cast(Any, ring).addition()
        assert multiplication.operation is cast(Any, ring).multiplication()
        return self.ObjectType(_TopologicalRingData(ring, space, addition, multiplication))

    def homomorphism(
        self,
        source: TopologicalRingsCategory.ObjectType,
        target: TopologicalRingsCategory.ObjectType,
        ring_map: MorphismCategory.ObjectType,
        continuous_map: TopologicalSpacesCategory.MorphismType,
    ) -> TopologicalRingsCategory.MorphismType:
        rings = _rings()
        assert ring_map.domain() is source.ring() and ring_map.codomain() is target.ring()
        assert continuous_map.domain() is source.space() and continuous_map.codomain() is target.space()
        underlying_ring_map = rings.forgetful().on_morphism(ring_map)
        assert ask(underlying_ring_map == continuous_map.underlying_map()) is True
        return cast(
            TopologicalRingsCategory.MorphismType,
            cast(Any, self).MorphismType(
                domain=source,
                codomain=target,
                data=(ring_map, continuous_map),
            ),
        )

    def construct_identity(
        self,
        member_object: TopologicalRingsCategory.ObjectType,
    ) -> TopologicalRingsCategory.MorphismType:
        return self.homomorphism(
            member_object,
            member_object,
            _rings().morphism_category(1)(member_object.ring(), member_object.ring()).one(),
            TopologicalSpaces().morphism_category(1)(member_object.space(), member_object.space()).one(),
        )

    def composite(
        self,
        second: TopologicalRingsCategory.MorphismType,
        first: TopologicalRingsCategory.MorphismType,
    ) -> TopologicalRingsCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.homomorphism(
            first.domain(),
            second.codomain(),
            second.ring_map() * first.ring_map(),
            second.continuous_map() * first.continuous_map(),
        )

    def __repr__(self) -> str:
        return "TopologicalRings"


@cached_function(key=identity_key)
def TopologicalRings() -> TopologicalRingsCategory:
    return TopologicalRingsCategory()
