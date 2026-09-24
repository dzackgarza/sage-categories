"""Ringed spaces and morphisms with sheaf action retained as natural transformations."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from typing import Any, cast

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.leaf_categories import MorphismDataCategory
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.geometry._ring_categories import commutative_rings as _rings
from sage_categories.geometry.sheaves import RingSheaf
from sage_categories.geometry.spaces import (
    TopologicalSpacesCategory,
    _topological_space_projection,
)

__all__ = ["RingedSpaces", "RingedSpacesCategory"]


type SheafComponentRule[OpenKey: Hashable] = Callable[[OpenKey], MorphismCategory.ObjectType]


@dataclass(frozen=True, eq=False, slots=True)
class _RingedSpaceData[OpenKey: Hashable]:
    space: TopologicalSpacesCategory.ObjectType[OpenKey]
    sheaf: RingSheaf[OpenKey]


class RingedSpacesCategory(MorphismDataCategory):
    """Spaces equipped with sheaves of commutative rings."""

    class ObjectType[OpenKey: Hashable = Hashable]:
        def __init__(self, data: _RingedSpaceData[OpenKey]) -> None:
            self._space, self._sheaf = data.space, data.sheaf

        def space(self) -> TopologicalSpacesCategory.ObjectType[OpenKey]:
            return self._space

        def sheaf(self) -> RingSheaf[OpenKey]:
            return self._sheaf

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: tuple[TopologicalSpacesCategory.MorphismType, NaturalTransformation]) -> None:
            self._continuous_map, self._sheaf_map = data

        def continuous_map(self) -> TopologicalSpacesCategory.MorphismType:
            return self._continuous_map

        def sheaf_map(self) -> NaturalTransformation:
            return self._sheaf_map

    def to_spaces(self) -> Functor:
        return next(functor for functor in self.selected_functors() if functor.codomain() is self._space_category())

    def _space_category(self):
        from sage_categories.geometry.spaces import TopologicalSpaces

        return TopologicalSpaces()

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), _topological_space_projection(self))

    def __call__[OpenKey: Hashable](
        self,
        space: TopologicalSpacesCategory.ObjectType[OpenKey],
        sheaf: RingSheaf[OpenKey],
    ) -> RingedSpacesCategory.ObjectType[OpenKey]:
        assert sheaf.presheaf.space is space
        return self.ObjectType(_RingedSpaceData(space, sheaf))

    def homomorphism[SourceKey: Hashable, TargetKey: Hashable](
        self,
        source: RingedSpacesCategory.ObjectType[SourceKey],
        target: RingedSpacesCategory.ObjectType[TargetKey],
        continuous: TopologicalSpacesCategory.MorphismType,
        component_rule: SheafComponentRule[TargetKey],
    ) -> RingedSpacesCategory.MorphismType:
        """A morphism ``X -> Y`` with ``O_Y -> O_X (f^-1)^op`` as an actual natural transformation."""
        return self._morphism_from_data(
            source,
            target,
            self._ringed_morphism_data(source, target, continuous, component_rule),
        )

    def _ringed_morphism_data[SourceKey: Hashable, TargetKey: Hashable](
        self,
        source: RingedSpacesCategory.ObjectType[SourceKey],
        target: RingedSpacesCategory.ObjectType[TargetKey],
        continuous: TopologicalSpacesCategory.MorphismType,
        component_rule: SheafComponentRule[TargetKey],
    ) -> tuple[TopologicalSpacesCategory.MorphismType, NaturalTransformation]:
        assert continuous.domain() is source.space() and continuous.codomain() is target.space()
        inverse_op = cast(Any, continuous).inverse_image().op()
        target_sheaf = target.sheaf().presheaf.functor
        pushed_source = source.sheaf().presheaf.functor * inverse_op
        assert target_sheaf.domain() is pushed_source.domain() and target_sheaf.codomain() is pushed_source.codomain()

        def component(open_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            arrow = component_rule(target.sheaf().presheaf.open_key(open_object))
            assert arrow.domain() is target_sheaf.on_object(open_object)
            assert arrow.codomain() is pushed_source.on_object(open_object)
            return arrow

        # ``Mor(Fun(...))`` is the mathematical owner of natural transformations;
        # its component assignment is trusted (``specs/functor.md``, "Naturality is
        # trusted").  Do not enumerate the represented open category here: ringed-space
        # morphisms must also work for topologies supplied by ``from_open_category``.
        transformation = Mor(Fun(target_sheaf.domain(), _rings()))(target_sheaf, pushed_source)(component)
        return continuous, transformation

    def _identity_data(
        self,
        member_object: RingedSpacesCategory.ObjectType,
    ) -> tuple[TopologicalSpacesCategory.MorphismType, NaturalTransformation]:
        spaces = self._space_category()
        space = member_object.space()
        continuous = Mor(spaces)(space, space).one()
        sheaf = member_object.sheaf()

        def component(open_key: Hashable) -> MorphismCategory.ObjectType:
            ring = sheaf.presheaf.section_ring(open_key)
            return Mor(_rings())(ring, ring).one()

        return self._ringed_morphism_data(
            member_object,
            member_object,
            continuous,
            component,
        )

    def _composite_data(
        self,
        second: RingedSpacesCategory.MorphismType,
        first: RingedSpacesCategory.MorphismType,
    ) -> tuple[TopologicalSpacesCategory.MorphismType, NaturalTransformation]:
        source, target = first.domain(), second.codomain()
        continuous = second.continuous_map() * first.continuous_map()

        def component(target_key: Hashable) -> MorphismCategory.ObjectType:
            target_open = target.sheaf().presheaf.open_object(target_key)
            middle_open = second.continuous_map().inverse_image().on_object(target_open)
            second_component = second.sheaf_map().component(target_open)
            first_component = first.sheaf_map().component(middle_open)
            assert second_component.codomain() is first_component.domain()
            return first_component * second_component

        return self._ringed_morphism_data(
            source,
            target,
            continuous,
            component,
        )

    def __repr__(self) -> str:
        return "RingedSpaces"


def RingedSpaces() -> RingedSpacesCategory:
    return _RINGED_SPACES


_RINGED_SPACES = RingedSpacesCategory()
