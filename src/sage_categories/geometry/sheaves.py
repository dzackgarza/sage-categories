"""Commutative-ring presheaves on represented spaces, with owned restriction maps."""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from importlib import import_module
from typing import Any, cast

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import ask
from sage_categories.geometry.spaces import TopologicalSpacesCategory

__all__ = ["RingPresheaf", "ring_presheaf"]


def _rings() -> Any:
    return import_module("sage_categories.cat.structured_objects").Rings(Sets).Commutative()


def _open_data(open_object: CategoryOfCategories.ElementType) -> frozenset[Hashable]:
    return cast(frozenset[Hashable], cast(Any, open_object).point().datum())


def _opposite_original(arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    return cast(MorphismCategory.ObjectType, cast(Any, arrow).original())


@dataclass(frozen=True, eq=False, slots=True)
class RingPresheaf:
    """A retained functor ``O(X)^op -> CRing`` with exact owned section rings."""

    space: TopologicalSpacesCategory.ObjectType
    functor: Functor
    sections: Mapping[frozenset[Hashable], CategoryOfCategories.ElementType]

    def section_ring(self, open_set: frozenset[Hashable]) -> CategoryOfCategories.ElementType:
        return self.sections[open_set]

    def restriction(
        self,
        larger: frozenset[Hashable],
        smaller: frozenset[Hashable],
    ) -> MorphismCategory.ObjectType:
        """The owned ring map ``F(larger) -> F(smaller)`` for ``smaller <= larger``."""
        opens = self.space.open_category()
        inclusion = Mor(opens)(self.space.open_object(smaller), self.space.open_object(larger))()
        return cast(MorphismCategory.ObjectType, self.functor.on_morphism(opposite_morphism(inclusion)))


def ring_presheaf(
    space: TopologicalSpacesCategory.ObjectType,
    sections: Mapping[frozenset[Hashable], CategoryOfCategories.ElementType],
    restrictions: Mapping[
        tuple[frozenset[Hashable], frozenset[Hashable]],
        MorphismCategory.ObjectType,
    ],
) -> RingPresheaf:
    """Construct a commutative-ring presheaf after checking its restriction identities and composites."""
    opens = tuple(point.datum() for point in cast(Any, space.opens()).carrier())
    assert set(sections) == set(opens)
    rings = _rings()
    assert all(section in rings for section in sections.values())

    comparable = tuple((larger, smaller) for larger in opens for smaller in opens if smaller <= larger)
    assert set(restrictions) == set(comparable)
    for larger, smaller in comparable:
        arrow = restrictions[(larger, smaller)]
        assert arrow.domain() is sections[larger] and arrow.codomain() is sections[smaller]
    for open_set in opens:
        assert ask(restrictions[(open_set, open_set)] == Mor(rings)(sections[open_set], sections[open_set]).one()) is True
    for largest in opens:
        for middle in opens:
            for smallest in opens:
                if smallest <= middle <= largest:
                    assert ask(
                        restrictions[(middle, smallest)] * restrictions[(largest, middle)]
                        == restrictions[(largest, smallest)]
                    ) is True

    source = space.open_category().op()

    def on_object(open_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return sections[_open_data(open_object)]

    def on_morphism(opposite_inclusion: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        inclusion = _opposite_original(opposite_inclusion)
        smaller = _open_data(inclusion.domain())
        larger = _open_data(inclusion.codomain())
        return restrictions[(larger, smaller)]

    return RingPresheaf(space, Fun(source, rings)(on_object, on_morphism), sections)
