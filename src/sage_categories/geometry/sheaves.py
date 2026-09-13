"""Commutative-ring presheaves on represented spaces, with owned restriction maps."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from typing import Any, cast

from sage_categories.cat.category import Category, CategoryOfCategories
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


def _apply_ring_map(
    arrow: MorphismCategory.ObjectType,
    section: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    return cast(CategoryOfCategories.ElementType, cast(Any, arrow)(section))


@dataclass(frozen=True, eq=False, slots=True)
class RingPresheaf[OpenKey: Hashable]:
    """A retained functor ``O(X)^op -> CRing`` on an arbitrary owned open category."""

    space: object
    opens: Category
    functor: Functor
    open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType]
    open_key_rule: Callable[[CategoryOfCategories.ElementType], OpenKey]

    def open_object(self, key: OpenKey) -> CategoryOfCategories.ElementType:
        return self.open_object_rule(key)

    def open_key(self, open_object: CategoryOfCategories.ElementType) -> OpenKey:
        return self.open_key_rule(open_object)

    def section_ring(self, open_set: OpenKey) -> CategoryOfCategories.ElementType:
        return cast(
            CategoryOfCategories.ElementType,
            self.functor.on_object(self.open_object(open_set)),
        )

    def restriction(
        self,
        larger: OpenKey,
        smaller: OpenKey,
    ) -> MorphismCategory.ObjectType:
        """The owned ring map ``F(larger) -> F(smaller)`` for ``smaller <= larger``."""
        inclusion = Mor(self.opens)(self.open_object(smaller), self.open_object(larger))()
        return cast(
            MorphismCategory.ObjectType,
            self.functor.on_morphism(opposite_morphism(inclusion)),
        )


type GluingRule[OpenKey: Hashable] = Callable[
    [
        OpenKey,
        tuple[OpenKey, ...],
        tuple[CategoryOfCategories.ElementType, ...],
    ],
    CategoryOfCategories.ElementType,
]


def _validate_gluing_family(
    presheaf: RingPresheaf[frozenset[Hashable]],
    open_set: frozenset[Hashable],
    cover: tuple[frozenset[Hashable], ...],
    local_sections: tuple[CategoryOfCategories.ElementType, ...],
) -> None:
    """Check that one finite local family is well typed and agrees on every overlap."""
    assert cover and frozenset().union(*cover) == open_set
    assert len(cover) == len(local_sections)
    for member, section in zip(cover, local_sections, strict=True):
        assert section.parent() is presheaf.section_ring(member)
    for left_index, left in enumerate(cover):
        for right_index, right in enumerate(cover):
            overlap = left & right
            left_restriction = _apply_ring_map(presheaf.restriction(left, overlap), local_sections[left_index])
            right_restriction = _apply_ring_map(
                presheaf.restriction(right, overlap),
                local_sections[right_index],
            )
            assert ask(left_restriction == right_restriction) is True


def _verify_gluing_result(
    presheaf: RingPresheaf[frozenset[Hashable]],
    open_set: frozenset[Hashable],
    cover: tuple[frozenset[Hashable], ...],
    local_sections: tuple[CategoryOfCategories.ElementType, ...],
    global_section: CategoryOfCategories.ElementType,
) -> None:
    """Check restriction and uniqueness of one proposed global section."""
    global_ring = presheaf.section_ring(open_set)
    assert global_section.parent() is global_ring
    for member, local in zip(cover, local_sections, strict=True):
        assert ask(_apply_ring_map(presheaf.restriction(open_set, member), global_section) == local) is True

    carrier = _ambient_rings().forgetful().on_object(global_ring)
    matching = []
    for candidate in tuple(carrier):
        point = cast(Any, global_ring).point(candidate.datum())
        if all(ask(_apply_ring_map(presheaf.restriction(open_set, member), point) == local) is True for member, local in zip(cover, local_sections, strict=True)):
            matching.append(point)
    assert len(matching) == 1 and ask(matching[0] == global_section) is True


@dataclass(frozen=True, eq=False, slots=True)
class RingSheaf[OpenKey: Hashable]:
    """A ring presheaf with retained finite-cover gluing."""

    presheaf: RingPresheaf[OpenKey]
    gluing_rule: GluingRule[OpenKey]

    def glue(
        self: RingSheaf[frozenset[Hashable]],
        open_set: frozenset[Hashable],
        cover: tuple[frozenset[Hashable], ...],
        local_sections: tuple[CategoryOfCategories.ElementType, ...],
    ) -> CategoryOfCategories.ElementType:
        """Glue one compatible finite family and verify its unique global section."""
        _validate_gluing_family(self.presheaf, open_set, cover, local_sections)
        global_section = self.gluing_rule(open_set, cover, local_sections)
        _verify_gluing_result(self.presheaf, open_set, cover, local_sections, global_section)
        return global_section


def ring_presheaf(
    space: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]],
    sections: Mapping[frozenset[Hashable], CategoryOfCategories.ElementType],
    restrictions: Mapping[
        tuple[frozenset[Hashable], frozenset[Hashable]],
        MorphismCategory.ObjectType,
    ],
) -> RingPresheaf[frozenset[Hashable]]:
    """Construct a commutative-ring presheaf after checking its restriction identities and composites."""
    rings = _validate_ring_presheaf_data(space, sections, restrictions)

    source = space.open_category().op()

    def on_object(
        open_object: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return sections[_open_data(open_object)]

    def on_morphism(
        opposite_inclusion: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        inclusion = cast(
            MorphismCategory.ObjectType,
            cast(Any, opposite_inclusion).original(),
        )
        smaller = _open_data(inclusion.domain())
        larger = _open_data(inclusion.codomain())
        return restrictions[(larger, smaller)]

    return ring_presheaf_from_functor(
        space,
        space.open_category(),
        Fun(source, rings)(on_object, on_morphism),
        space.open_object,
        _open_data,
    )


def _validate_ring_presheaf_data(
    space: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]],
    sections: Mapping[frozenset[Hashable], CategoryOfCategories.ElementType],
    restrictions: Mapping[
        tuple[frozenset[Hashable], frozenset[Hashable]],
        MorphismCategory.ObjectType,
    ],
) -> Category:
    """Validate the section rings and contravariant restriction calculus for a finite open family."""
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
    return rings


def ring_presheaf_from_functor[OpenKey: Hashable](
    space: TopologicalSpacesCategory.ObjectType[OpenKey],
    opens: Category,
    functor: Functor,
    open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType],
    open_key_rule: Callable[[CategoryOfCategories.ElementType], OpenKey],
) -> RingPresheaf[OpenKey]:
    """Retain an arbitrary represented ring presheaf from its actual contravariant functor."""
    assert functor.domain() is opens.op()
    assert functor.codomain() is _rings()
    return RingPresheaf(space, opens, functor, open_object_rule, open_key_rule)


def ring_sheaf[OpenKey: Hashable](presheaf: RingPresheaf[OpenKey], gluing_rule: GluingRule[OpenKey]) -> RingSheaf[OpenKey]:
    """Retain the supplied finite-cover gluing operation on this ring presheaf."""
    return RingSheaf(presheaf, gluing_rule)
