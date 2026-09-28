"""Commutative-ring presheaves on represented spaces, with owned restriction maps."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from typing import Any, cast

from sage_categories.cat.calculus import (
    finite_product_data,
    finite_product_morphism,
    finite_product_projection,
    natural_isomorphism,
)
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.choices import ChosenConstruction
from sage_categories.cat.constructions import UniversalPresentation
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.limit_basis import (
    equalizer_factor,
    equalizer_presentation,
    parallel_pair,
)
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import Unknown, ask
from sage_categories.geometry._ring_categories import (
    commutative_rings as _rings,
)
from sage_categories.geometry.spaces import TopologicalSpacesCategory
from sage_categories.order.posets import Posets

__all__ = [
    "RingPresheaf",
    "RingSheaf",
    "descent_chart_comparison",
    "descent_lift",
    "descent_map",
    "descent_projection",
    "descent_restriction",
    "descent_section_ring",
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


def _descent_presentation_for_component(
    section_ring: CategoryOfCategories.ElementType,
    local_ring: CategoryOfCategories.ElementType,
    component_index: int,
) -> UniversalPresentation:
    """Select the descent presentation whose local product has this component."""
    family = _rings().Equalizers()
    source_vertex = Cat().WalkingParallelPair()(0)

    def has_component(diagram: Functor) -> bool:
        local_product = diagram.on_object(source_vertex)
        if local_product is local_ring:
            return component_index == 0
        if ask(_rings().Products().membership_proposition(local_product)) is not True:
            return False
        return local_product.product_projection(component_index).codomain() is local_ring

    diagrams = tuple(diagram for diagram in family.presenting_diagrams(section_ring) if has_component(diagram))
    assert len(diagrams) == 1, f"{section_ring!r} has {len(diagrams)} descent presentations with component {component_index} = {local_ring!r}"
    return family.universal_data(diagrams[0])


def _local_projection(
    local_product: CategoryOfCategories.ElementType,
    local_ring: CategoryOfCategories.ElementType,
    component_index: int,
) -> MorphismCategory.ObjectType:
    """One local-product projection, including the singleton-product identity."""
    match local_product is local_ring:
        case True:
            assert component_index == 0
            return Mor(_rings())(local_ring, local_ring).one()
        case False:
            return local_product.product_projection(component_index)


def descent_section_ring(
    open_key: Hashable,
    local_rings: tuple[CategoryOfCategories.ElementType, ...],
    overlap_restrictions: Callable[[int, int], tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]],
) -> CategoryOfCategories.ElementType:
    """The generic ring-limit of compatible local sections for one finite cover."""

    def construct() -> CategoryOfCategories.ElementType:
        rings = _rings()
        assert local_rings, "a finite descent cover must have at least one local ring"
        local_data = finite_product_data(rings, local_rings)
        local_product = local_data.apex()
        local_projections = tuple(finite_product_projection(local_data, index) for index in range(len(local_rings)))
        overlaps: list[tuple[int, int, MorphismCategory.ObjectType, MorphismCategory.ObjectType]] = []
        for left_index in range(len(local_rings)):
            for right_index in range(left_index + 1, len(local_rings)):
                left_map, right_map = overlap_restrictions(left_index, right_index)
                assert left_map.codomain() is right_map.codomain()
                overlaps.append((left_index, right_index, left_map, right_map))

        match overlaps:
            case []:
                first = second = Mor(rings)(local_product, local_product).one()
            case _:
                overlap_rings = tuple(left_map.codomain() for _, _, left_map, _ in overlaps)
                overlap_data = finite_product_data(rings, overlap_rings)
                first = finite_product_morphism(
                    overlap_data,
                    local_product,
                    tuple(left_map * local_projections[left_index] for left_index, _, left_map, _ in overlaps),
                )
                second = finite_product_morphism(
                    overlap_data,
                    local_product,
                    tuple(right_map * local_projections[right_index] for _, right_index, _, right_map in overlaps),
                )

        diagram = parallel_pair(first, second)
        family = rings.Limits(diagram.domain())
        section_ring = family(diagram)
        return section_ring

    return _FINITE_DESCENT_SECTION_RINGS(_rings(), (open_key,), construct)


def descent_restriction(
    larger_key: Hashable,
    smaller_key: Hashable,
    source_ring: CategoryOfCategories.ElementType,
    target_ring: CategoryOfCategories.ElementType,
    component_restrictions: tuple[MorphismCategory.ObjectType, ...],
) -> MorphismCategory.ObjectType:
    """Restrict through the generic product/equalizer presentations."""
    _ = (larger_key, smaller_key)
    source_rings = tuple(restriction.domain() for restriction in component_restrictions)
    local_product = finite_product_data(_rings(), source_rings).apex()
    source = equalizer_presentation(_rings(), source_ring, local_product)
    local_product = source.diagram().on_object(source.diagram().domain().generator("f").domain())
    inclusion = source.leg(source.diagram().domain().generator("f").domain())
    components = tuple(restriction * _local_projection(local_product, restriction.domain(), index) * inclusion for index, restriction in enumerate(component_restrictions))
    return descent_map(smaller_key, source_ring, target_ring, components)


def descent_projection(
    open_key: Hashable,
    section_ring: CategoryOfCategories.ElementType,
    local_ring: CategoryOfCategories.ElementType,
    component_index: int,
) -> MorphismCategory.ObjectType:
    """Project using the retained equalizer inclusion followed by a product projection."""
    _ = open_key
    data = _descent_presentation_for_component(section_ring, local_ring, component_index)
    inclusion = data.leg(data.diagram().domain().generator("f").domain())
    local_product = inclusion.codomain()
    projection = _local_projection(local_product, local_ring, component_index) * inclusion
    assert projection.codomain() is local_ring
    return projection


def descent_lift(
    open_key: Hashable,
    local_ring: CategoryOfCategories.ElementType,
    section_ring: CategoryOfCategories.ElementType,
    component_maps: tuple[MorphismCategory.ObjectType, ...],
    component_index: int,
) -> MorphismCategory.ObjectType:
    """Lift one chart section to the uniquely compatible represented family."""
    lift = descent_map(open_key, local_ring, section_ring, component_maps)
    projection = descent_projection(open_key, section_ring, local_ring, component_index)
    _rings().retain_inverses(projection, lift)
    return lift


def descent_map(
    open_key: Hashable,
    source_ring: CategoryOfCategories.ElementType,
    target_ring: CategoryOfCategories.ElementType,
    component_maps: tuple[MorphismCategory.ObjectType, ...],
) -> MorphismCategory.ObjectType:
    """Map into a compatible-family ring through its retained limit mediator."""
    _ = open_key
    target_rings = tuple(component.codomain() for component in component_maps)
    product_data = finite_product_data(_rings(), target_rings)
    target_product = product_data.apex()
    target = equalizer_presentation(_rings(), target_ring, target_product)
    into_product = finite_product_morphism(product_data, source_ring, component_maps)
    assert into_product.codomain() is target_product
    return equalizer_factor(target, into_product)


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
    assert frozenset().union(*cover) == open_set
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
    """Check that one selected amalgamation has the required restrictions.

    Uniqueness is the trusted sheaf declaration, not a computation by exhaustive
    enumeration of the global section ring.
    """
    global_ring = presheaf.section_ring(open_set)
    assert global_section.parent() is global_ring
    for member, local in zip(cover, local_sections, strict=True):
        assert ask(_apply_ring_map(presheaf.restriction(open_set, member), global_section) == local) is True


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
    opens = tuple(point.datum() for point in Posets().to_sets().on_object(cast(Any, space.opens())))
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


_FINITE_DESCENT_SECTION_RINGS = ChosenConstruction()
