"""Commutative-ring presheaves on represented spaces, with owned restriction maps."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from typing import Any, cast

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import ask
from sage_categories.geometry._ring_categories import (
    commutative_rings as _rings,
)
from sage_categories.geometry._ring_categories import (
    rings as _ambient_rings,
)
from sage_categories.geometry.spaces import TopologicalSpacesCategory

__all__ = [
    "RingPresheaf",
    "RingSheaf",
    "ring_presheaf",
    "ring_presheaf_from_functor",
    "ring_sheaf",
]


def _open_data(open_object: CategoryOfCategories.ElementType) -> frozenset[Hashable]:
    return cast(frozenset[Hashable], cast(Any, open_object).point().datum())


def _opposite_original(
    arrow: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    return cast(MorphismCategory.ObjectType, cast(Any, arrow).original())


def _apply_ring_map(
    arrow: MorphismCategory.ObjectType,
    section: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    return cast(CategoryOfCategories.ElementType, cast(Any, arrow)(section))


@dataclass(frozen=True, eq=False, slots=True)
class RingPresheaf:
    """A retained functor ``O(X)^op -> CRing`` on an arbitrary owned open category."""

    space: object
    opens: Any
    functor: Functor
    open_object_rule: Callable[[object], CategoryOfCategories.ElementType]
    open_key_rule: Callable[[CategoryOfCategories.ElementType], object]

    def open_object(self, key: object) -> CategoryOfCategories.ElementType:
        return self.open_object_rule(key)

    def open_key(self, open_object: CategoryOfCategories.ElementType) -> object:
        return self.open_key_rule(open_object)

    def section_ring(self, open_set: object) -> CategoryOfCategories.ElementType:
        return cast(
            CategoryOfCategories.ElementType,
            self.functor.on_object(self.open_object(open_set)),
        )

    def restriction(
        self,
        larger: object,
        smaller: object,
    ) -> MorphismCategory.ObjectType:
        """The owned ring map ``F(larger) -> F(smaller)`` for ``smaller <= larger``."""
        inclusion = Mor(self.opens)(self.open_object(smaller), self.open_object(larger))()
        return cast(
            MorphismCategory.ObjectType,
            self.functor.on_morphism(opposite_morphism(inclusion)),
        )


type GluingRule = Callable[
    [
        frozenset[Hashable],
        tuple[frozenset[Hashable], ...],
        tuple[CategoryOfCategories.ElementType, ...],
    ],
    CategoryOfCategories.ElementType,
]


@dataclass(frozen=True, eq=False, slots=True)
class RingSheaf:
    """A ring presheaf with retained finite-cover gluing."""

    presheaf: RingPresheaf
    gluing_rule: GluingRule

    def glue(
        self,
        open_set: frozenset[Hashable],
        cover: tuple[frozenset[Hashable], ...],
        local_sections: tuple[CategoryOfCategories.ElementType, ...],
    ) -> CategoryOfCategories.ElementType:
        """Glue one compatible finite family and verify its unique global section."""
        assert cover and frozenset().union(*cover) == open_set
        assert len(cover) == len(local_sections)
        for member, section in zip(cover, local_sections, strict=True):
            assert section.parent() is self.presheaf.section_ring(member)
        for left_index, left in enumerate(cover):
            for right_index, right in enumerate(cover):
                overlap = left & right
                left_restriction = _apply_ring_map(self.presheaf.restriction(left, overlap), local_sections[left_index])
                right_restriction = _apply_ring_map(
                    self.presheaf.restriction(right, overlap),
                    local_sections[right_index],
                )
                assert ask(left_restriction == right_restriction) is True

        global_section = self.gluing_rule(open_set, cover, local_sections)
        global_ring = self.presheaf.section_ring(open_set)
        assert global_section.parent() is global_ring
        for member, local in zip(cover, local_sections, strict=True):
            assert ask(_apply_ring_map(self.presheaf.restriction(open_set, member), global_section) == local) is True

        carrier = _ambient_rings().forgetful().on_object(global_ring)
        candidates = tuple(carrier)
        matching = []
        for candidate in candidates:
            point = cast(Any, global_ring).point(candidate.datum())
            if all(ask(_apply_ring_map(self.presheaf.restriction(open_set, member), point) == local) is True for member, local in zip(cover, local_sections, strict=True)):
                matching.append(point)
        assert len(matching) == 1 and ask(matching[0] == global_section) is True
        return global_section


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
                    assert ask(restrictions[(middle, smallest)] * restrictions[(largest, middle)] == restrictions[(largest, smallest)]) is True

    source = space.open_category().op()

    def on_object(
        open_object: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return sections[_open_data(open_object)]

    def on_morphism(
        opposite_inclusion: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        inclusion = _opposite_original(opposite_inclusion)
        smaller = _open_data(inclusion.domain())
        larger = _open_data(inclusion.codomain())
        return restrictions[(larger, smaller)]

    return ring_presheaf_from_functor(
        space,
        space.open_category(),
        Fun(source, rings)(on_object, on_morphism),
        lambda key: space.open_object(cast(frozenset[Hashable], key)),
        lambda open_object: _open_data(open_object),
    )


def ring_presheaf_from_functor(
    space: object,
    opens: Any,
    functor: Functor,
    open_object_rule: Callable[[object], CategoryOfCategories.ElementType],
    open_key_rule: Callable[[CategoryOfCategories.ElementType], object],
) -> RingPresheaf:
    """Retain an arbitrary represented ring presheaf from its actual contravariant functor."""
    assert functor.domain() is opens.op()
    assert functor.codomain() is _rings()
    return RingPresheaf(space, opens, functor, open_object_rule, open_key_rule)


def ring_sheaf(presheaf: RingPresheaf, gluing_rule: GluingRule) -> RingSheaf:
    """Retain the supplied finite-cover gluing operation on this ring presheaf."""
    return RingSheaf(presheaf, gluing_rule)
