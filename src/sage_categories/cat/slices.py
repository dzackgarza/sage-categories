"""Slices, coslices, and comma categories as strict pullbacks; their fibration lifts; the subobject families (D06, D10, POL-CAT-026/095, POL-FUN-031).

``C.SliceOver(x)`` is the strict pullback in ``Cat()`` of ``ev_1: Fun([1], C) -> C``
along the point ``x: 1 -> C``: its objects are the pairs ``(f, *)`` with
``ev_1(f) == x``, decided by identity of retained objects and ``Unknown``
otherwise (D02, D17).  ``C.CosliceUnder(x)`` is the pullback of ``ev_0``.  A comma
category ``(F, G)`` for ``F: A -> C`` and ``G: B -> C`` is the pullback of
``(ev_0, ev_1): Fun([1], C) -> C * C`` along ``F * G`` (Mathlib
``CategoryTheory.Comma``: objects are triples ``(left, right, hom: L left -> R
right)`` and morphisms are commuting squares; inspected 2026-08-27).  Each retains
its pullback projections; the varying object is the composite with ``ev_0``
(slice) or ``ev_1`` (coslice), and that composite is the slice's one selected
structural functor: an object over ``x`` is an object of ``C`` with a morphism to
``x`` (POL-CAT-047).

The fixed slice projection ``C.SliceOver(x) -> C`` is the category of elements of
``Mor(C)(-, x)`` and a discrete fibration for every ``C``: the cartesian lift of
``f: y -> z`` at ``(z, p)`` is ``f: (y, p * f) -> (z, p)`` by precomposition (nLab
"discrete fibration", inspected 2026-08-27: "the representable presheaf on an
object X corresponds to the canonical functor B/X -> B from the slice category
over X").  Dually the coslice projection is a discrete opfibration with
cocartesian lifts by postcomposition.  The lifts of ``ev_1`` and ``ev_0``
themselves are retained by ``Fun([1], C)`` (``cat/diagrams.py``); the total
category and its fiber carry distinct lift data (D10).

Objects of ``C.SliceOver(x)`` are the generalized elements of ``x`` (D06): a
morphism ``t: T -> x`` or an element with that defining morphism is accepted as
the object ``(t, *)``, and is a member by the same decision.

``C.Subobjects()`` is the full subcategory of ``Fun([1], C)`` on the monomorphisms,
decided through ``Mor(C).Monomorphisms()``; ``C.Subobjects()(x)`` is its fiber over
``x``, the full subcategory of ``C.SliceOver(x)`` on ``(m, *)`` with ``m`` a
monomorphism (POL-FUN-013/014).  ``CoveringObjects()`` uses epimorphisms: a
covering object of ``y`` is the pair ``(X, p: X -> y)``, not ``p`` alone
(POL-CAT-026).  ``Superobjects()`` and ``CoveredObjects()`` are the coslice duals.
"""

from __future__ import annotations

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat.cat_constructions import PairMorphism, PairObject, PullbackCategory, images_agree, strict_pullback
from sage_categories.cat.category import Category, member
from sage_categories.cat.constructions import cone
from sage_categories.cat.diagrams import cospan_diagram, sequence_position
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.properties import FullSubcategory
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory, Role, role_of

__all__ = [
    "CosliceCategory",
    "MorphismPropertyFamily",
    "MorphismPropertyFiber",
    "SliceCategory",
    "comma_category",
    "coslice_under",
    "slice_over",
]


def _walking_arrow() -> Category:
    return Cat().Simplex(1)


def _star() -> ObjectOfCategory:
    return Cat().Terminal()(0)


# ``slice_member(t, C/x)``: ``t`` is an object of the slice: a generalized element of
# ``x`` (an element, or a morphism into ``x``), or a constructed pair whose images agree.
slice_member = Predicate("slice_member", 2, False)


def _slice_member_by_codomain(candidate: CategoryPoint, slice_category: Category) -> Decision:
    base, fixed = slice_category.base_of_slice(), slice_category.fixed_object()
    if role_of(candidate) is Role.ELEMENT:
        return ask(candidate.parent() == fixed)
    if candidate in base.morphism_category(1):
        return ask(candidate.codomain() == fixed)
    return ask(member(candidate, slice_category) & images_agree(candidate, slice_category))


slice_member.register_handler(_slice_member_by_codomain)


class SliceCategory(PullbackCategory):
    """``C.SliceOver(x)``: the strict pullback of ``ev_1`` along ``x: 1 -> C``, with the generalized elements of ``x`` as objects."""

    def __init__(self, base: Category, fixed: ObjectOfCategory) -> None:
        self._base_of_slice = base
        self._fixed = fixed
        self._slice_projection: MonoDict = MonoDict()
        arrows = Fun(_walking_arrow(), base)
        super().__init__(arrows.evaluation(_walking_arrow()(1)), base.point_functor(fixed))

    def base_of_slice(self) -> Category:
        return self._base_of_slice

    def fixed_object(self) -> ObjectOfCategory:
        return self._fixed

    def projection(self) -> Functor:
        """The fixed slice projection ``C.SliceOver(x) -> C``: ``ev_0`` after the pullback projection to ``Fun([1], C)``."""
        if self not in self._slice_projection:
            arrows = Fun(_walking_arrow(), self._base_of_slice)
            self._slice_projection[self] = arrows.evaluation(_walking_arrow()(0)) * self.first_projection()
        return self._slice_projection[self]

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.projection(),)

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return slice_member(candidate, self)

    def __call__(self, value: CategoryPoint | tuple[CategoryPoint, ObjectOfCategory]) -> PairObject:
        """The object ``(t, *)`` of a morphism ``t: T -> x``, of an element with that defining morphism, or of an explicit pair."""
        match value:
            case (first, second):
                return super().__call__((first, second))
        morphism = value if value in self._base_of_slice.morphism_category(1) else value.defining_morphism()
        return super().__call__((morphism, _star()))

    def cartesian_lift(self, morphism: MorphismOfCategory, member_object: PairObject) -> PairMorphism:
        """The cartesian lift of ``f: y -> z`` at ``(z, p)``: ``f: (y, p * f) -> (z, p)`` by precomposition."""
        structure = member_object.first()
        assert morphism.codomain() is structure.domain(), f"{morphism!r} does not end at the varying object of {member_object!r}"
        composite = structure * morphism
        components = {0: morphism, 1: self._fixed.identity()}
        arrows = Fun(_walking_arrow(), self._base_of_slice)
        square = arrows.morphism_category(1)(composite, structure)(lambda vertex: components[_walking_arrow().label(vertex)])
        return self.construct_morphism(self((composite, _star())), member_object, (square, _star().identity()))

    def __repr__(self) -> str:
        return f"{self._base_of_slice!r}.SliceOver({self._fixed!r})"


class CosliceCategory(PullbackCategory):
    """``C.CosliceUnder(x)``: the strict pullback of ``ev_0`` along ``x: 1 -> C``."""

    def __init__(self, base: Category, fixed: ObjectOfCategory) -> None:
        self._base_of_slice = base
        self._fixed = fixed
        self._coslice_projection: MonoDict = MonoDict()
        arrows = Fun(_walking_arrow(), base)
        super().__init__(arrows.evaluation(_walking_arrow()(0)), base.point_functor(fixed))

    def base_of_slice(self) -> Category:
        return self._base_of_slice

    def fixed_object(self) -> ObjectOfCategory:
        return self._fixed

    def projection(self) -> Functor:
        """The fixed coslice projection ``C.CosliceUnder(x) -> C``: ``ev_1`` after the pullback projection to ``Fun([1], C)``."""
        if self not in self._coslice_projection:
            arrows = Fun(_walking_arrow(), self._base_of_slice)
            self._coslice_projection[self] = arrows.evaluation(_walking_arrow()(1)) * self.first_projection()
        return self._coslice_projection[self]

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.projection(),)

    def __call__(self, value: MorphismOfCategory | tuple[MorphismOfCategory, ObjectOfCategory]) -> PairObject:
        """The object ``(t, *)`` of a morphism ``t: x -> T`` or of an explicit pair."""
        match value:
            case (first, second):
                return super().__call__((first, second))
        return super().__call__((value, _star()))

    def cocartesian_lift(self, morphism: MorphismOfCategory, member_object: PairObject) -> PairMorphism:
        """The cocartesian lift of ``f: y -> z`` at ``(y, p)``: ``f: (y, p) -> (z, f * p)`` by postcomposition."""
        structure = member_object.first()
        assert morphism.domain() is structure.codomain(), f"{morphism!r} does not start at the varying object of {member_object!r}"
        composite = morphism * structure
        components = {0: self._fixed.identity(), 1: morphism}
        arrows = Fun(_walking_arrow(), self._base_of_slice)
        square = arrows.morphism_category(1)(structure, composite)(lambda vertex: components[_walking_arrow().label(vertex)])
        return self.construct_morphism(member_object, self((composite, _star())), (square, _star().identity()))

    def __repr__(self) -> str:
        return f"{self._base_of_slice!r}.CosliceUnder({self._fixed!r})"


def slice_over(base: Category, fixed: ObjectOfCategory) -> SliceCategory:
    """``C.SliceOver(x)`` with its pullback presentation retained in ``Cat().Pullbacks()``."""
    apex = SliceCategory(base, fixed)
    strict_pullback(cospan_diagram(Cat(), apex.first_functor(), apex.second_functor()), apex)
    return apex


def coslice_under(base: Category, fixed: ObjectOfCategory) -> CosliceCategory:
    """``C.CosliceUnder(x)`` with its pullback presentation retained in ``Cat().Pullbacks()``."""
    apex = CosliceCategory(base, fixed)
    strict_pullback(cospan_diagram(Cat(), apex.first_functor(), apex.second_functor()), apex)
    return apex


# -- comma categories ------------------------------------------------------------------------

_commas: TripleDict = TripleDict(weak_values=False)


def _pair_functor(first: Functor, second: Functor) -> Functor:
    """``F * G: A * B -> C * D``: the mediator of the cone ``(F * pi_A, G * pi_B)`` over the product ``C * D``."""
    source = Cat().Products()((first.domain(), second.domain()))
    target = Cat().Products()((first.codomain(), second.codomain()))
    legs = {0: first * source.product_projection(0), 1: second * source.product_projection(1)}
    return target.universal_morphism(cone(target.diagram(), source.apex(), lambda vertex: legs[sequence_position(vertex)]))


def _endpoint_functor(base: Category) -> Functor:
    """``(ev_0, ev_1): Fun([1], C) -> C * C``: the mediator of the cone of the two evaluations."""
    arrows = Fun(_walking_arrow(), base)
    target = Cat().Products()((base, base))
    legs = {0: arrows.evaluation(_walking_arrow()(0)), 1: arrows.evaluation(_walking_arrow()(1))}
    return target.universal_morphism(cone(target.diagram(), arrows, lambda vertex: legs[sequence_position(vertex)]))


def comma_category(first: Functor, second: Functor) -> PullbackCategory:
    """The comma category ``(F, G)``: the pullback of ``(ev_0, ev_1)`` along ``F * G``, retained per pair; objects ``((a, b), f: F a -> G b)``."""
    assert first.codomain() is second.codomain(), f"{first!r} and {second!r} have different codomains"
    key = (first, second, Cat())
    if key not in _commas:
        _commas[key] = Cat().Pullbacks()(cospan_diagram(Cat(), _pair_functor(first, second), _endpoint_functor(first.codomain()))).apex()
    return _commas[key]


# -- the subobject families (POL-SCOPE-003, POL-CAT-026, POL-FUN-013) ------------------------

# ``has_morphism_property(x, S)``: the morphism that ``x`` denotes in the family ``S``
# lies in the property subcategory of ``Mor(C)`` that ``S`` selects.
has_morphism_property = Predicate("has_morphism_property", 2, False)


def _has_morphism_property(candidate: CategoryPoint, family: Category) -> Decision:
    return ask(family.property_category().predicate()(family.morphism_of(candidate)))


has_morphism_property.register_handler(_has_morphism_property)

_FAMILIES: dict[str, tuple[str, bool]] = {
    "Subobjects": ("Monomorphisms", True),
    "Superobjects": ("Monomorphisms", False),
    "CoveringObjects": ("Epimorphisms", True),
    "CoveredObjects": ("Epimorphisms", False),
}


class MorphismPropertyFamily(FullSubcategory[[NaturalTransformation], []]):
    """``C.Subobjects()`` and its three relatives: the full subcategory of ``Fun([1], C)`` on the morphisms with the selected property."""

    def __init__(self, base: Category, name: str) -> None:
        self._base_of_family = base
        self._name = name
        self._fibers: MonoDict = MonoDict()
        super().__init__(Fun(_walking_arrow(), base))

    def base_of_family(self) -> Category:
        return self._base_of_family

    def over(self) -> bool:
        """Whether the fibers live in slices (over) rather than coslices (under)."""
        return _FAMILIES[self._name][1]

    def property_category(self) -> Category:
        morphisms = self._base_of_family.morphism_category(1)
        return morphisms.Monomorphisms() if _FAMILIES[self._name][0] == "Monomorphisms" else morphisms.Epimorphisms()

    def morphism_of(self, candidate: CategoryPoint) -> MorphismOfCategory:
        """The morphism of ``C`` that an object of ``Fun([1], C)`` denotes."""
        if candidate in self._base_of_family.morphism_category(1):
            return candidate
        return self._ambient.diagram(candidate).on_morphism(_walking_arrow().generator("0->1"))

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return self._ambient.membership_proposition(candidate) & has_morphism_property(candidate, self)

    def __call__(self, value: CategoryPoint) -> CategoryPoint:
        """``C.Subobjects()(x)`` is the fiber over (or under) the object ``x``; on a morphism, the trusted assertion of the property."""
        if value in self._base_of_family:
            if value not in self._fibers:
                fiber_ambient = self._base_of_family.SliceOver(value) if self.over() else self._base_of_family.CosliceUnder(value)
                self._fibers[value] = MorphismPropertyFiber(self, fiber_ambient)
            return self._fibers[value]
        assert ask(has_morphism_property(value, self)) is not False, f"{value!r} is not in {self.property_category()!r}"
        return value

    def __repr__(self) -> str:
        return f"{self._base_of_family!r}.{self._name}()"


class MorphismPropertyFiber(FullSubcategory[[tuple[MorphismOfCategory, MorphismOfCategory]], []]):
    """``C.Subobjects()(x)``: the full subcategory of ``C.SliceOver(x)`` (or of the coslice) on the pairs whose morphism has the property."""

    def __init__(self, family: MorphismPropertyFamily, fiber_ambient: Category) -> None:
        self._family = family
        super().__init__(fiber_ambient)

    def family(self) -> MorphismPropertyFamily:
        return self._family

    def property_category(self) -> Category:
        return self._family.property_category()

    def morphism_of(self, candidate: CategoryPoint) -> MorphismOfCategory:
        """The morphism of ``C`` that a slice object, a morphism into ``x``, or an element of ``x`` denotes."""
        if role_of(candidate) is Role.ELEMENT:
            return candidate.defining_morphism()
        if candidate in self._family.base_of_family().morphism_category(1):
            return candidate
        return candidate.first()

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return self._ambient.membership_proposition(candidate) & has_morphism_property(candidate, self)

    def __call__(self, value: CategoryPoint) -> PairObject:
        """The pair ``(m, *)`` of a morphism with the property; the writer's assertion is trusted unless decided false."""
        assert ask(has_morphism_property(value, self)) is not False, f"{value!r} is not in {self.property_category()!r}"
        return self._ambient(value)

    def __repr__(self) -> str:
        return f"{self._family!r}({self._ambient.fixed_object()!r})"
