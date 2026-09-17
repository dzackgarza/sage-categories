"""Locally ringed spaces over the generic represented sheaf/stalk calculus."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass

from sympy import true

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.leaf_categories import MorphismDataCategory
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.predicates import Axiom, Proposition
from sage_categories.geometry._ring_categories import commutative_rings as _rings
from sage_categories.geometry.ringed_spaces import RingedSpaces, RingedSpacesCategory
from sage_categories.geometry.spaces import TopologicalSpaces
from sage_categories.geometry.stalks import ring_stalk, ringed_stalk_map

__all__ = ["LocallyRingedSpaces", "LocallyRingedSpacesCategory"]


type LocalRingRule = Callable[
    [CategoryOfCategories.ElementType, CategoryOfCategories.ElementType],
    Proposition,
]
type LocalMapRule = Callable[
    [CategoryOfCategories.ElementType, MorphismCategory.ObjectType],
    Proposition,
]
type StalkRule = Callable[
    [CategoryOfCategories.ElementType],
    CategoryOfCategories.ElementType,
]
type StalkMapRule = Callable[
    [CategoryOfCategories.ElementType],
    MorphismCategory.ObjectType,
]


@dataclass(frozen=True, eq=False, slots=True)
class _LocallyRingedSpaceData:
    ringed_space: RingedSpacesCategory.ObjectType
    stalk_rule: StalkRule
    local_ring_rule: LocalRingRule


@dataclass(frozen=True, eq=False, slots=True)
class _LocallyRingedMorphismData:
    ringed_map: RingedSpacesCategory.MorphismType
    stalk_map_rule: StalkMapRule
    local_map_rule: LocalMapRule


def _ringed_identity(
    ringed_space: RingedSpacesCategory.ObjectType,
) -> RingedSpacesCategory.MorphismType:
    spaces = TopologicalSpaces()
    space = ringed_space.space()
    continuous = Mor(spaces)(space, space).one()
    sheaf = ringed_space.sheaf()

    def component(open_key: Hashable) -> MorphismCategory.ObjectType:
        ring = sheaf.presheaf.section_ring(open_key)
        return Mor(_rings())(ring, ring).one()

    return RingedSpaces().homomorphism(
        ringed_space,
        ringed_space,
        continuous,
        component,
    )


def _ringed_composite(
    second: RingedSpacesCategory.MorphismType,
    first: RingedSpacesCategory.MorphismType,
) -> RingedSpacesCategory.MorphismType:
    assert first.codomain() is second.domain()
    source, target = first.domain(), second.codomain()
    continuous = second.continuous_map() * first.continuous_map()

    def component(target_key: Hashable) -> MorphismCategory.ObjectType:
        target_open = target.sheaf().presheaf.open_object(target_key)
        middle_open = second.continuous_map().inverse_image().on_object(target_open)
        second_component = second.sheaf_map().component(target_open)
        first_component = first.sheaf_map().component(middle_open)
        assert second_component.codomain() is first_component.domain()
        return first_component * second_component

    return RingedSpaces().homomorphism(
        source,
        target,
        continuous,
        component,
    )


class LocallyRingedSpacesCategory(MorphismDataCategory):
    """Ringed spaces with local stalks and stalkwise-local morphisms."""

    Scheme = Axiom()

    class ObjectType:
        def __init__(self, data: _LocallyRingedSpaceData) -> None:
            self._locally_ringed_data = data

        def ringed_space(self) -> RingedSpacesCategory.ObjectType:
            return self._locally_ringed_data.ringed_space

        def space(self):
            return self.ringed_space().space()

        def sheaf(self):
            return self.ringed_space().sheaf()

        def stalk(
            self,
            point: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            return self._locally_ringed_data.stalk_rule(point)

        def local_ring_condition(
            self,
            point: CategoryOfCategories.ElementType,
        ) -> Proposition:
            """The retained proposition that the stalk at ``point`` is a local ring."""
            return self._locally_ringed_data.local_ring_rule(point, self.stalk(point))

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: _LocallyRingedMorphismData) -> None:
            self._locally_ringed_map_data = data

        def ringed_map(self) -> RingedSpacesCategory.MorphismType:
            return self._locally_ringed_map_data.ringed_map

        def continuous_map(self) -> MorphismCategory.ObjectType:
            return self.ringed_map().continuous_map()

        def sheaf_map(self):
            return self.ringed_map().sheaf_map()

        def stalk_map(
            self,
            source_point: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            return self._locally_ringed_map_data.stalk_map_rule(source_point)

        def local_map_condition(
            self,
            source_point: CategoryOfCategories.ElementType,
        ) -> Proposition:
            """The retained proposition that the induced stalk map is local."""
            return self._locally_ringed_map_data.local_map_rule(
                source_point,
                self.stalk_map(source_point),
            )

    def to_ringed_spaces(self) -> Functor:
        return next(
            functor
            for functor in self.selected_functors()
            if functor.codomain() is RingedSpaces()
        )

    def structure_functors(self) -> tuple[Functor, ...]:
        forgetful = Fun(self, RingedSpaces()).Faithful()(
            lambda value: value.ringed_space(),
            lambda arrow: arrow.ringed_map(),
        )
        return (*super().structure_functors(), forgetful)

    def __call__(
        self,
        ringed_space: RingedSpacesCategory.ObjectType,
        local_ring_rule: LocalRingRule,
    ) -> LocallyRingedSpacesCategory.ObjectType:
        return self.with_stalks(
            ringed_space,
            lambda point: ring_stalk(ringed_space.sheaf(), point),
            local_ring_rule,
        )

    def with_stalks(
        self,
        ringed_space: RingedSpacesCategory.ObjectType,
        stalk_rule: StalkRule,
        local_ring_rule: LocalRingRule,
    ) -> LocallyRingedSpacesCategory.ObjectType:
        """Construct from a supplied stalk evaluator with the same public LRS surface."""
        assert ringed_space in RingedSpaces()
        return self.ObjectType(
            _LocallyRingedSpaceData(ringed_space, stalk_rule, local_ring_rule)
        )

    def homomorphism(
        self,
        source: LocallyRingedSpacesCategory.ObjectType,
        target: LocallyRingedSpacesCategory.ObjectType,
        ringed_map: RingedSpacesCategory.MorphismType,
        local_map_rule: LocalMapRule,
    ) -> LocallyRingedSpacesCategory.MorphismType:
        return self.homomorphism_with_stalks(
            source,
            target,
            ringed_map,
            lambda point: ringed_stalk_map(ringed_map, point),
            local_map_rule,
        )

    def homomorphism_with_stalks(
        self,
        source: LocallyRingedSpacesCategory.ObjectType,
        target: LocallyRingedSpacesCategory.ObjectType,
        ringed_map: RingedSpacesCategory.MorphismType,
        stalk_map_rule: StalkMapRule,
        local_map_rule: LocalMapRule,
    ) -> LocallyRingedSpacesCategory.MorphismType:
        """Construct from a supplied induced-stalk-map evaluator."""
        assert ringed_map.domain() is source.ringed_space()
        assert ringed_map.codomain() is target.ringed_space()
        return self._morphism_from_data(
            source,
            target,
            _LocallyRingedMorphismData(ringed_map, stalk_map_rule, local_map_rule),
        )

    def _identity_data(
        self,
        member_object: LocallyRingedSpacesCategory.ObjectType,
    ) -> _LocallyRingedMorphismData:
        def identity_stalk_map(
            point: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            stalk = member_object.stalk(point)
            return Mor(_rings())(stalk, stalk).one()

        return _LocallyRingedMorphismData(
            _ringed_identity(member_object.ringed_space()),
            identity_stalk_map,
            lambda _point, _stalk_map: true,
        )

    def _composite_data(
        self,
        second: LocallyRingedSpacesCategory.MorphismType,
        first: LocallyRingedSpacesCategory.MorphismType,
    ) -> _LocallyRingedMorphismData:
        first_map, second_map = first.ringed_map(), second.ringed_map()

        def local_at(
            source_point: CategoryOfCategories.ElementType,
            _stalk_map: MorphismCategory.ObjectType,
        ) -> Proposition:
            middle_point = first_map.continuous_map().underlying_map()(source_point)
            return first.local_map_condition(source_point) & second.local_map_condition(
                middle_point
            )

        def stalk_map_at(
            source_point: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            middle_point = first_map.continuous_map().underlying_map()(source_point)
            return first.stalk_map(source_point) * second.stalk_map(middle_point)

        return _LocallyRingedMorphismData(
            _ringed_composite(second_map, first_map),
            stalk_map_at,
            local_at,
        )

    def __repr__(self) -> str:
        return "LocallyRingedSpaces"


def LocallyRingedSpaces() -> LocallyRingedSpacesCategory:
    return _LOCALLY_RINGED_SPACES


_LOCALLY_RINGED_SPACES = LocallyRingedSpacesCategory()
