"""Slices, coslices, and comma categories as strict pullbacks; their fibration lifts; the subobject families (POL-CAT-026/095, POL-FUN-013/031, POL-SCOPE-003).

``C.SliceOver(x)`` is the strict pullback in ``Cat()`` of ``ev_1: Fun([1], C) -> C``
along the point ``x: 1 -> C``: its objects are the pairs ``(f, *)`` with
``ev_1(f) == x``, decided by identity of retained objects and ``Unknown``
otherwise (``specs/functor.md``, "Slices and coslices").  ``C.CosliceUnder(x)`` is
the pullback of ``ev_0``.  A comma category ``(F, G)`` for ``F: A -> C`` and
``G: B -> C`` is the pullback of ``(ev_0, ev_1): Fun([1], C) -> C * C`` along
``F * G`` (Mathlib ``CategoryTheory.Comma``: objects are triples ``(left, right,
hom: L left -> R right)`` and morphisms are commuting squares; inspected
2026-08-27).  Each retains its pullback projections; the varying object is the
composite with ``ev_0`` (slice) or ``ev_1`` (coslice), retained as the fixed
projection to ``C`` and selected by no structural graph: an object over ``x`` is
a pair, not an object of ``C``, and a generalized element of ``x`` does not
acquire the object surface of ``C`` (POL-CAT-047, POL-FUN-031).

The fixed slice projection ``C.SliceOver(x) -> C`` is the category of elements of
``Mor(C)(-, x)`` and a discrete fibration for every ``C``: the cartesian lift of
``f: y -> z`` at ``(z, p)`` is ``f: (y, p * f) -> (z, p)`` by precomposition (nLab
"discrete fibration", inspected 2026-08-27: "the representable presheaf on an
object X corresponds to the canonical functor B/X -> B from the slice category
over X").  Dually the coslice projection is a discrete opfibration with
cocartesian lifts by postcomposition.  Each slice registers its lift rule on its
fixed projection, which retains the lifts (``Functor.cartesian_lift``); the
evaluations ``ev_1`` and ``ev_0`` retain their own lifts (``cat/diagrams.py``), so
the total category and its fiber carry distinct lift data (POL-FUN-031).

Objects of ``C.SliceOver(x)`` are the generalized elements of ``x``
(``specs/functor.md``, "Slices and coslices"; AGENTS.md, "Core categorical
architecture"): a morphism ``t: T -> x`` or an element with that defining
morphism is accepted as the object ``(t, *)``, and is a member by the same
decision.

``C.Subobjects(x)`` is ``C.SliceOver(x).Monomorphisms()``: the property subcategory
``Mor(C).Monomorphisms()`` pulled back along the retained defining-arrow functor of the
slice, which is its pullback projection to the category of arrows (POL-CAT-092,
POL-FUN-013/014).  A full subcategory is identity on values, so that pullback is the full
subcategory of the slice on the objects whose defining arrow has the property
(``specs/functor.md``, "Fixed-object construction categories"), and ``SliceProperty``
retains both projections of the square.  Whether an arrow has the property is the
containment question ``Mor(C).Monomorphisms()`` declares, asked of that arrow; nothing
here reaches for that category's predicate object (POL-CAT-043, POL-CAT-044).
``C.CoveringObjects(y)`` uses epimorphisms: a covering object of ``y`` is the pair
``(X, p: X -> y)``, not ``p`` alone (POL-CAT-026).  ``C.Superobjects(x)`` and
``C.CoveredObjects(x)`` are the coslice duals.  The ambient category named in the call
fixes the role of ``x``, which is why these are methods of a category and not of the
object.

``C.Subobjects(P)`` for a product ``P`` is ``SubobjectsOfProduct``, whose objects read
each component as ``P.product_projection(i) after j`` through their own monomorphism
``j``, so a subobject of a product has every component without a leaf repeating those
maps (POL-CAT-094).  The slice names that class when its fixed object is a product, so
the method exists exactly where it applies and no subobject asserts its own
applicability (POL-KERNEL-025).
"""

from __future__ import annotations

from collections.abc import Hashable

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat.cat_constructions import PullbackCategory, images_agree, strict_pullback
from sage_categories.cat.category import Category, member
from sage_categories.cat.constructions import cone
from sage_categories.cat.diagrams import cospan_diagram, sequence_position
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.properties import FullSubcategory
from sage_categories.kernel.decisions import Decision
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory, Role, role_of

__all__ = [
    "CosliceCategory",
    "SliceCategory",
    "SliceProperty",
    "SubobjectsOfProduct",
    "comma_category",
    "coslice_under",
    "slice_over",
]


def _walking_arrow() -> Category:
    return Cat().Simplex(1)


def _star() -> ObjectOfCategory:
    return Cat().Terminal()(0)


def _star_identity() -> MorphismOfCategory:
    """``1_*``: the unit of ``End_1(*)``, the fixed component of a slice morphism (POL-CAT-023)."""
    star = _star()
    return star.category().morphism_category(1)(star, star).one()


def _denoted_morphism(candidate: CategoryPoint) -> CategoryPoint:
    """The morphism a candidate denotes: the defining morphism of a generalized element, else the candidate itself."""
    if role_of(candidate) is Role.ELEMENT:
        return candidate.defining_morphism()
    return candidate


# ``slice_member(t, C/x)``: ``t`` is an object of the slice or coslice: a morphism of
# ``C`` (or a generalized element denoting one) whose fixed end equals ``x``, or a
# constructed pair whose images agree.
slice_member = Predicate("slice_member", 2, False)


def _slice_member_by_fixed_end(candidate: CategoryPoint, slice_category: Category) -> Decision:
    morphism = _denoted_morphism(candidate)
    if morphism in slice_category.base_of_slice().morphism_category(1):
        return ask(slice_category.fixed_end(morphism) == slice_category.fixed_object())
    return ask(member(candidate, slice_category) & images_agree(candidate, slice_category))


slice_member.register_handler(_slice_member_by_fixed_end)


class SliceLikeCategory(PullbackCategory):
    """The pullback of an evaluation ``ev_k: Fun([1], C) -> C`` along ``x: 1 -> C``; ``k = 1`` is the slice, ``k = 0`` the coslice."""

    # An object is a pullback pair whose fixed end is ``x``: an arrow of ``C`` with one
    # endpoint pinned.  The arrow is its whole content, so the varying object is read as
    # ``ev_k`` after the projection and is not a second datum.
    ObjectType = PullbackCategory.ObjectType
    ElementType = PullbackCategory.ElementType
    MorphismType = PullbackCategory.MorphismType

    def __init__(self, base: Category, fixed: ObjectOfCategory, fixed_label: int) -> None:
        self._base_of_slice = base
        self._fixed = fixed
        self._fixed_label = fixed_label
        self._properties: MonoDict = MonoDict()
        squares = Fun(_walking_arrow(), base)
        super().__init__(squares.evaluation(_walking_arrow()(fixed_label)), base.point_functor(fixed))
        self._fixed_projection = squares.evaluation(_walking_arrow()(1 - fixed_label)) * self.first_projection()
        self.retain_lifts(self._fixed_projection)

    def retain_lifts(self, fixed_projection: Functor) -> None:
        """Retain on the fixed projection the lifts that make it a discrete fibration (slice) or opfibration (coslice)."""
        raise AssertionError(f"{self!r} declares no lifts")

    def base_of_slice(self) -> Category:
        return self._base_of_slice

    def fixed_object(self) -> ObjectOfCategory:
        return self._fixed

    def fixed_end(self, morphism: MorphismOfCategory) -> ObjectOfCategory:
        """The end of a morphism of ``C`` that an object must fix: the codomain over ``x``, the domain under ``x``."""
        if self._fixed_label == 1:
            return morphism.codomain()
        return morphism.domain()

    def fixed_projection(self) -> Functor:
        """The fixed projection to ``C``: the evaluation at the varying end after the pullback projection to ``Fun([1], C)``, retained once."""
        return self._fixed_projection

    def defining_arrow(self) -> Functor:
        """The retained functor to ``Fun([1], C)`` returning the defining morphism of an object: the pullback projection (POL-CAT-092)."""
        return self.first_projection()

    def defining_arrow_of(self, candidate: CategoryPoint) -> MorphismOfCategory:
        """The defining morphism of a slice object, of a morphism of ``C``, or of a generalized element denoting one."""
        morphism = _denoted_morphism(candidate)
        if morphism in self._base_of_slice.morphism_category(1):
            return morphism
        return self.defining_arrow().on_object(candidate)

    def property_type(self, property_category: Category) -> type[SliceProperty]:
        """The class that implements one of this slice's property subcategories."""
        return SliceProperty

    def _property(self, property_category: Category) -> Category:
        """The pullback of a property subcategory of ``Mor(C)`` along the defining-arrow functor, retained per property."""
        if property_category not in self._properties:
            self._properties[property_category] = self.property_type(property_category)(self, property_category)
        return self._properties[property_category]

    def Monomorphisms(self) -> Category:
        return self._property(self._base_of_slice.morphism_category(1).Monomorphisms())

    def Epimorphisms(self) -> Category:
        return self._property(self._base_of_slice.morphism_category(1).Epimorphisms())

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return slice_member(candidate, self)

    def __call__(self, value: CategoryPoint | tuple[CategoryPoint, ObjectOfCategory]) -> PullbackCategory.ObjectType:
        """The object ``(t, *)`` of a morphism ``t`` of ``C``, of a generalized element denoting one, or of an explicit pair."""
        match value:
            case (first, second):
                return super().__call__((first, second))
        if is_placed(value, self):
            return value
        morphism = _denoted_morphism(value)
        assert morphism in self._base_of_slice.morphism_category(1), f"{value!r} denotes no morphism of {self._base_of_slice!r}"
        return super().__call__((morphism, _star()))

    def _square(self, source: MorphismOfCategory, target: MorphismOfCategory, varying: MorphismOfCategory) -> NaturalTransformation:
        """The commuting square from ``source`` to ``target`` whose component at the fixed end is the identity of ``x``."""
        fixed = self._fixed
        components = {self._fixed_label: fixed.category().morphism_category(1)(fixed, fixed).one(), 1 - self._fixed_label: varying}
        squares = Fun(_walking_arrow(), self._base_of_slice)
        return squares.morphism_category(1)(source, target)(lambda vertex: components[_walking_arrow().label(vertex)])


class SliceCategory(SliceLikeCategory):
    """``C.SliceOver(x)``: the strict pullback of ``ev_1`` along ``x: 1 -> C``, with the generalized elements of ``x`` as objects."""

    # An object is a morphism ``a -> x``, a generalized element of ``x``, whose varying
    # object is its domain.
    ObjectType = SliceLikeCategory.ObjectType
    ElementType = SliceLikeCategory.ElementType
    MorphismType = SliceLikeCategory.MorphismType

    def __init__(self, base: Category, fixed: ObjectOfCategory) -> None:
        super().__init__(base, fixed, 1)

    def property_type(self, property_category: Category) -> type[SliceProperty]:
        """The subobjects of a product state their components; the subobjects of any other object have no such method (POL-CAT-094)."""
        monomorphisms = self._base_of_slice.morphism_category(1).Monomorphisms()
        if property_category is monomorphisms and self._fixed in self._base_of_slice.Products():
            return SubobjectsOfProduct
        return SliceProperty

    def retain_lifts(self, fixed_projection: Functor) -> None:
        fixed_projection.retain_cartesian_lifts(self._precomposition_lift)

    def _precomposition_lift(self, morphism: MorphismOfCategory, member_object: PullbackCategory.ObjectType) -> PullbackCategory.MorphismType:
        """The cartesian lift of ``f: y -> z`` at ``(z, p)`` for the fixed projection: ``f: (y, p * f) -> (z, p)`` by precomposition."""
        structure = member_object.first()
        assert morphism.codomain() is structure.domain(), f"{morphism!r} does not end at the varying object of {member_object!r}"
        composite = structure * morphism
        square = self._square(composite, structure, morphism)
        return self.construct_morphism(self((composite, _star())), member_object, (square, _star_identity()))

    def __repr__(self) -> str:
        return f"{self._base_of_slice!r}.SliceOver({self._fixed!r})"


class CosliceCategory(SliceLikeCategory):
    """``C.CosliceUnder(x)``: the strict pullback of ``ev_0`` along ``x: 1 -> C``."""

    # An object is a morphism ``x -> a``, whose varying object is its codomain.
    ObjectType = SliceLikeCategory.ObjectType
    ElementType = SliceLikeCategory.ElementType
    MorphismType = SliceLikeCategory.MorphismType

    def __init__(self, base: Category, fixed: ObjectOfCategory) -> None:
        super().__init__(base, fixed, 0)

    def retain_lifts(self, fixed_projection: Functor) -> None:
        fixed_projection.retain_cocartesian_lifts(self._postcomposition_lift)

    def _postcomposition_lift(self, morphism: MorphismOfCategory, member_object: PullbackCategory.ObjectType) -> PullbackCategory.MorphismType:
        """The cocartesian lift of ``f: y -> z`` at ``(y, p)`` for the fixed projection: ``f: (y, p) -> (z, f * p)`` by postcomposition."""
        structure = member_object.first()
        assert morphism.domain() is structure.codomain(), f"{morphism!r} does not start at the varying object of {member_object!r}"
        composite = morphism * structure
        square = self._square(structure, composite, morphism)
        return self.construct_morphism(member_object, self((composite, _star())), (square, _star_identity()))

    def __repr__(self) -> str:
        return f"{self._base_of_slice!r}.CosliceUnder({self._fixed!r})"


def slice_over(base: Category, fixed: ObjectOfCategory) -> SliceCategory:
    """``C.SliceOver(x)``: the chosen pullback of its cospan, retained in ``Cat().Pullbacks()``."""
    apex = SliceCategory(base, fixed)
    return strict_pullback(cospan_diagram(Cat(), apex.first_functor(), apex.second_functor()), apex)


def coslice_under(base: Category, fixed: ObjectOfCategory) -> CosliceCategory:
    """``C.CosliceUnder(x)``: the chosen pullback of its cospan, retained in ``Cat().Pullbacks()``."""
    apex = CosliceCategory(base, fixed)
    return strict_pullback(cospan_diagram(Cat(), apex.first_functor(), apex.second_functor()), apex)


# -- comma categories ------------------------------------------------------------------------

_commas: TripleDict = TripleDict(weak_values=False)


def _pair_functor(first: Functor, second: Functor) -> Functor:
    """``F * G: A * B -> C * D``: the mediator of the cone ``(F * pi_A, G * pi_B)`` over the product ``C * D``."""
    source = Cat().Products()((first.domain(), second.domain()))
    target = Cat().Products()((first.codomain(), second.codomain()))
    legs = {0: first * source.product_projection(0), 1: second * source.product_projection(1)}
    return target.universal_morphism(cone(target.product_factors(), source, lambda vertex: legs[sequence_position(vertex)]))


def _endpoint_functor(base: Category) -> Functor:
    """``(ev_0, ev_1): Fun([1], C) -> C * C``: the mediator of the cone of the two evaluations."""
    squares = Fun(_walking_arrow(), base)
    target = Cat().Products()((base, base))
    legs = {0: squares.evaluation(_walking_arrow()(0)), 1: squares.evaluation(_walking_arrow()(1))}
    return target.universal_morphism(cone(target.product_factors(), squares, lambda vertex: legs[sequence_position(vertex)]))


def comma_category(first: Functor, second: Functor) -> PullbackCategory:
    """The comma category ``(F, G)``: the pullback of ``(ev_0, ev_1)`` along ``F * G``, retained per pair; objects ``((a, b), f: F a -> G b)``."""
    assert first.codomain() is second.codomain(), f"{first!r} and {second!r} have different codomains"
    key = (first, second, Cat())
    if key not in _commas:
        _commas[key] = Cat().Pullbacks()(cospan_diagram(Cat(), _pair_functor(first, second), _endpoint_functor(first.codomain())))
    return _commas[key]


# -- the fixed-object construction categories (POL-CAT-092/094, POL-CAT-026, POL-FUN-013) ----

# ``has_morphism_property(x, S)``: the defining arrow of ``x`` is an object of the
# property subcategory of ``Mor(C)`` that ``S`` pulls back.
has_morphism_property = Predicate("has_morphism_property", 2, False)


def _has_morphism_property(candidate: CategoryPoint, family: Category) -> Decision:
    """The containment question the property subcategory declares, asked of the defining arrow (POL-CAT-043, POL-CAT-044)."""
    return ask(family.property_category().membership_proposition(family.defining_arrow_of(candidate)))


has_morphism_property.register_handler(_has_morphism_property)


class SliceProperty(FullSubcategory[[tuple[MorphismOfCategory, MorphismOfCategory]], []]):
    """``C.SliceOver(x).Monomorphisms()`` and its relatives: a property subcategory of ``Mor(C)`` pulled back along the defining-arrow functor.

    The property subcategory is identity on values, so the pullback is the full
    subcategory of the slice or coslice on the objects whose defining arrow has the
    property (POL-CAT-092, ``specs/functor.md``, "Fixed-object construction
    categories").  It retains both projections of that square: the subcategory
    monomorphism into the slice, and ``defining_arrow()``, the composite carrying an
    object to its arrow.
    """

    # A subobject of ``x`` is the pair ``(a, j: a -> x)`` with ``j`` monic, and the pair
    # is the object of the slice, so the property adds nothing to it.  ``j`` is read
    # through the retained ``defining_arrow()`` functor rather than stored again.
    ObjectType = FullSubcategory.ObjectType
    ElementType = FullSubcategory.ElementType
    MorphismType = FullSubcategory.MorphismType

    def __init__(self, ambient: SliceLikeCategory, property_category: Category) -> None:
        self._property_category = property_category
        self._retained: MonoDict = MonoDict()
        super().__init__(ambient)

    def property_category(self) -> Category:
        return self._property_category

    def base_of_slice(self) -> Category:
        return self._ambient.base_of_slice()

    def subcategory_monomorphism(self) -> Functor:
        """This pullback's projection to the slice: the identity-on-values monomorphism, retained once."""
        (monomorphism,) = self.structure_functors()
        return monomorphism

    def defining_arrow(self) -> Functor:
        """This pullback's projection to the arrows: the slice's defining-arrow functor after the subcategory monomorphism, retained once."""
        if self not in self._retained:
            self._retained[self] = self._ambient.defining_arrow() * self.subcategory_monomorphism()
        return self._retained[self]

    def defining_arrow_of(self, candidate: CategoryPoint) -> MorphismOfCategory:
        return self._ambient.defining_arrow_of(candidate)

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return self._ambient.membership_proposition(candidate) & has_morphism_property(candidate, self)

    def __call__(self, value: CategoryPoint) -> PullbackCategory.ObjectType:
        """The pair ``(m, *)`` of a morphism with the property: the trusted constructor of the property on ``m`` (POL-MATH-037), rejected only when decided false."""
        assert ask(has_morphism_property(value, self)) is not False, f"{value!r} is not in {self._property_category!r}"
        self._property_category(self.defining_arrow_of(value))
        member_object = self._ambient(value)
        refine(member_object, self)
        return member_object

    def __repr__(self) -> str:
        return f"{self._ambient!r}.{self._property_category.name()}()"


class SubobjectsOfProduct(SliceProperty):
    """``C.Subobjects(P)`` for a product ``P``: the subobjects that read ``P``'s components through their own monomorphism.

    ``SliceCategory.property_type`` names this class exactly when the fixed object is a
    product, so the method belongs to the subobjects of a product and to no other
    subobject (POL-CAT-094, POL-KERNEL-025).
    """

    # The product structure of ``P`` adds no point and no triangle; it adds
    # ``product_projection`` on the subobject below.
    ElementType = SliceProperty.ElementType
    MorphismType = SliceProperty.MorphismType

    class ObjectType(ObjectOfCategory):
        """A subobject ``j: S -> P`` of a product: its components are ``P``'s projections after ``j``."""

        def product_projection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """``P.product_projection(i) after j``, so a subobject of a product has every component (POL-CAT-094)."""
            monomorphism = self.category().narrowing_base().defining_arrow_of(self)
            return monomorphism.codomain().product_projection(index) * monomorphism
