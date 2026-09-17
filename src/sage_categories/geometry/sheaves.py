"""Commutative-ring presheaves on represented spaces, with owned restriction maps."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from typing import Any, cast

from sympy import false, true

from sage_categories.algebra._certified_commutative_ring import (
    certified_commutative_ring,
)
from sage_categories.cat.calculus import natural_isomorphism
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import Unknown, ask
from sage_categories.cat.structured_objects import Rings
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
    "descent_chart_comparison",
    "descent_lift",
    "descent_map",
    "descent_projection",
    "descent_restriction",
    "descent_section_ring",
    "identity_sheaf_comparison",
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


def descent_section_ring(
    open_key: Hashable,
    local_rings: tuple[CategoryOfCategories.ElementType, ...],
    overlap_restrictions: Callable[
        [int, int], tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]
    ],
) -> CategoryOfCategories.ElementType:
    """The ring of compatible local sections for one represented finite cover.

    This is the sheaf-owner realization of the equalizer condition: the caller
    supplies the local rings and the two restriction maps to each pairwise
    overlap; the sheaf owner owns the compatibility equations, compatible-family
    ring, and all pointwise ring operations.
    """

    def construct() -> CategoryOfCategories.ElementType:
        def member(value: Hashable):
            match value:
                case (owner, values) if owner is open_key and isinstance(values, tuple):
                    if len(values) != len(local_rings):
                        return false
                    sections = cast(
                        tuple[CategoryOfCategories.ElementType, ...], values
                    )
                    if any(
                        not isinstance(section, CategoryOfCategories.ElementType)
                        or section.parent() is not ring
                        for section, ring in zip(sections, local_rings, strict=True)
                    ):
                        return false
                    for left_index in range(len(sections)):
                        for right_index in range(left_index + 1, len(sections)):
                            left_map, right_map = overlap_restrictions(
                                left_index, right_index
                            )
                            if (
                                ask(
                                    left_map(sections[left_index])
                                    == right_map(sections[right_index])
                                )
                                is not True
                            ):
                                return false
                    return true
                case _:
                    return false

        carrier = Sets.from_membership(member)

        def add(pair: tuple[Hashable, Hashable]) -> Hashable:
            left_owner, left_values = cast(tuple[object, tuple[Any, ...]], pair[0])
            right_owner, right_values = cast(tuple[object, tuple[Any, ...]], pair[1])
            assert left_owner is open_key and right_owner is open_key
            return open_key, tuple(
                left + right
                for left, right in zip(left_values, right_values, strict=True)
            )

        def multiply(pair: tuple[Hashable, Hashable]) -> Hashable:
            left_owner, left_values = cast(tuple[object, tuple[Any, ...]], pair[0])
            right_owner, right_values = cast(tuple[object, tuple[Any, ...]], pair[1])
            assert left_owner is open_key and right_owner is open_key
            return open_key, tuple(
                left * right
                for left, right in zip(left_values, right_values, strict=True)
            )

        zero = open_key, tuple(ring.zero() for ring in local_rings)
        one = open_key, tuple(ring.one() for ring in local_rings)
        return certified_commutative_ring(carrier, add, multiply, zero, one)

    from sage_categories.cat.assembly import chosen_construction

    return chosen_construction(
        _rings(),
        "finite-descent-section-ring",
        (open_key,),
        construct,
    )


def descent_restriction(
    larger_key: Hashable,
    smaller_key: Hashable,
    source_ring: CategoryOfCategories.ElementType,
    target_ring: CategoryOfCategories.ElementType,
    component_restrictions: tuple[MorphismCategory.ObjectType, ...],
) -> MorphismCategory.ObjectType:
    """Restrict a compatible family componentwise between represented opens."""
    source_carrier = Rings(Sets).forgetful().on_object(source_ring)
    target_carrier = Rings(Sets).forgetful().on_object(target_ring)

    def rule(value: Hashable) -> Hashable:
        owner, sections = cast(tuple[object, tuple[Any, ...]], value)
        assert owner is larger_key
        return (
            smaller_key,
            tuple(
                restriction(section)
                for restriction, section in zip(
                    component_restrictions, sections, strict=True
                )
            ),
        )

    underlying = Mor(Sets)(source_carrier, target_carrier)(rule)
    return _rings().restrict_morphism(
        Rings(Sets).homomorphism(source_ring, target_ring, underlying)
    )


def descent_projection(
    open_key: Hashable,
    section_ring: CategoryOfCategories.ElementType,
    local_ring: CategoryOfCategories.ElementType,
    component_index: int,
) -> MorphismCategory.ObjectType:
    """Project a compatible section family to one member of its cover."""
    source_carrier = Rings(Sets).forgetful().on_object(section_ring)
    target_carrier = Rings(Sets).forgetful().on_object(local_ring)

    def rule(value: Hashable) -> Hashable:
        owner, sections = cast(tuple[object, tuple[Any, ...]], value)
        assert owner is open_key
        return cast(CategoryOfCategories.ElementType, sections[component_index]).datum()

    underlying = Mor(Sets)(source_carrier, target_carrier)(rule)
    return _rings().restrict_morphism(
        Rings(Sets).homomorphism(section_ring, local_ring, underlying)
    )


def descent_lift(
    open_key: Hashable,
    local_ring: CategoryOfCategories.ElementType,
    section_ring: CategoryOfCategories.ElementType,
    component_maps: tuple[MorphismCategory.ObjectType, ...],
    component_index: int,
) -> MorphismCategory.ObjectType:
    """Lift one chart section to the uniquely compatible represented family."""
    source_carrier = Rings(Sets).forgetful().on_object(local_ring)
    target_carrier = Rings(Sets).forgetful().on_object(section_ring)

    def rule(value: Hashable) -> Hashable:
        section = local_ring.point(value)
        return open_key, tuple(component(section) for component in component_maps)

    underlying = Mor(Sets)(source_carrier, target_carrier)(rule)
    lift = _rings().restrict_morphism(
        Rings(Sets).homomorphism(local_ring, section_ring, underlying)
    )
    projection = descent_projection(open_key, section_ring, local_ring, component_index)
    _rings().retain_inverses(projection, lift)
    return lift


def descent_map(
    open_key: Hashable,
    source_ring: CategoryOfCategories.ElementType,
    target_ring: CategoryOfCategories.ElementType,
    component_maps: tuple[MorphismCategory.ObjectType, ...],
) -> MorphismCategory.ObjectType:
    """Map a section into a compatible-family ring via its chart components."""
    source_carrier = Rings(Sets).forgetful().on_object(source_ring)
    target_carrier = Rings(Sets).forgetful().on_object(target_ring)

    def rule(value: Hashable) -> Hashable:
        section = source_ring.point(value)
        return open_key, tuple(component(section) for component in component_maps)

    underlying = Mor(Sets)(source_carrier, target_carrier)(rule)
    return _rings().restrict_morphism(
        Rings(Sets).homomorphism(source_ring, target_ring, underlying)
    )


def descent_chart_comparison(
    local_opens: Category,
    local_sheaf: RingPresheaf,
    global_open: Callable[[CategoryOfCategories.ElementType], Hashable],
    global_ring: Callable[[Hashable], CategoryOfCategories.ElementType],
    restriction: Callable[[Hashable, Hashable], MorphismCategory.ObjectType],
    projection: Callable[[Hashable], MorphismCategory.ObjectType],
    lift: Callable[[Hashable], MorphismCategory.ObjectType],
) -> NaturalTransformation:
    """Compare a glued sheaf on one chart with the chart's own affine sheaf."""

    def on_object(
        open_object: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return global_ring(global_open(open_object))

    def on_morphism(
        opposite_inclusion: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        inclusion = opposite_morphism(opposite_inclusion)
        smaller = global_open(inclusion.domain())
        larger = global_open(inclusion.codomain())
        return restriction(smaller, larger)

    restricted = Fun(local_opens.op(), _rings())(on_object, on_morphism)
    return natural_isomorphism(
        restricted,
        local_sheaf.functor,
        lambda open_object: projection(global_open(open_object)),
        lambda open_object: lift(global_open(open_object)),
    )


def identity_sheaf_comparison(presheaf: RingPresheaf) -> NaturalTransformation:
    """The identity natural isomorphism of one represented ring presheaf."""

    def identity(
        open_object: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        ring = presheaf.functor.on_object(open_object)
        return Mor(_rings())(ring, ring).one()

    return natural_isomorphism(presheaf.functor, presheaf.functor, identity, identity)


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
        source, target = self.open_object(smaller), self.open_object(larger)
        hom = self.opens.hom_morphisms(source, target)
        if hom is Unknown:
            inclusion = Mor(self.opens)(source, target)()
        else:
            assert len(hom) == 1, f"open inclusion {source!r} -> {target!r} is not unique"
            inclusion = hom[0]
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
    """A ring presheaf declared to satisfy the sheaf condition.

    A selected gluing evaluator is additional computational data.  Finite
    represented topologies can retain one through :func:`ring_sheaf`; other
    sheaves need not manufacture an evaluator for an open representation that
    their backend does not use.
    """

    presheaf: RingPresheaf[OpenKey]
    gluing_rule: GluingRule[OpenKey] | None = None

    def glue(
        self: RingSheaf[frozenset[Hashable]],
        open_set: frozenset[Hashable],
        cover: tuple[frozenset[Hashable], ...],
        local_sections: tuple[CategoryOfCategories.ElementType, ...],
    ) -> CategoryOfCategories.ElementType:
        """Glue one compatible finite family and verify its unique global section."""
        match self.gluing_rule:
            case None:
                raise AssertionError("this sheaf has no selected gluing evaluator")
            case gluing_rule:
                selected_gluing = gluing_rule
        _validate_gluing_family(self.presheaf, open_set, cover, local_sections)
        global_section = selected_gluing(open_set, cover, local_sections)
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


def ring_sheaf[OpenKey: Hashable](
    presheaf: RingPresheaf[OpenKey],
    gluing_rule: GluingRule[OpenKey] | None = None,
) -> RingSheaf[OpenKey]:
    """Declare ``presheaf`` a sheaf and retain a gluing evaluator when supplied."""
    return RingSheaf(presheaf, gluing_rule)
