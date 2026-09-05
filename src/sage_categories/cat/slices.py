"""Slices, coslices, and comma categories as strict pullbacks.

``C.SliceOver(x)`` is the strict pullback of ``ev_1: Fun([1], C) -> C`` along the
point ``x: * -> C``. ``C.CosliceUnder(x)`` is the dual pullback of ``ev_0``.
An object is a morphism of ``C`` with one pinned endpoint, and a morphism is a
commuting triangle in ``C``.

The retained projections return the defining arrow and the varying object or
varying morphism. ``fixed_projection()`` is the selected structure functor.
The fixed projection also retains the cartesian or cocartesian lift data of the
slice or coslice.

``C.Subobjects(x)``, ``C.CoveringObjects(x)``, ``C.Superobjects(x)``, and
``C.CoveredObjects(x)`` are the monomorphism or epimorphism subcategories of
these slice or coslice categories. A comma category ``(F, G)`` is the owned
pullback of ``(ev_0, ev_1): Fun([1], C) -> C * C`` along ``F * G``.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING

from sympy import ask as sympy_ask

from sage_categories.cat.category import Category, member
from sage_categories.cat.comma import CommaCategory, CommaSpecialization, comma_objects
from sage_categories.cat.constructions import cone
from sage_categories.cat.diagrams import cospan_diagram, sequence_position
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import FullSubcategory
from sage_categories.cat.predicates import Predicate, Proposition, ask, register_handler
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.sage_runtime import MonoDict

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = [
    "CommaCategory",
    "SliceLikeCategory",
    "SliceProperty",
    "SubobjectsOfProduct",
    "comma_category",
    "coslice_under",
    "slice_over",
]


def _walking_arrow() -> Category:
    return Cat().Simplex(1)


def _star() -> CategoryOfCategories.ElementType:
    return Cat().Terminal()(0)


def _star_identity() -> MorphismCategory.ObjectType:
    """``1_*``: the unit of ``End_1(*)``, the image of every triangle under the projection to ``1`` (POL-CAT-023)."""
    star = _star()
    return star.category().morphism_category(1)(star, star).one()


def _denoted_morphism(candidate: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    """The morphism a candidate denotes: the defining morphism of a generalized element, else the candidate itself."""
    if candidate._is_element():
        return candidate.defining_morphism()
    return candidate


def _structure_of(member_object: SliceLikeCategory.ObjectType) -> MorphismCategory.ObjectType:
    return member_object.arrow()


def _varying_of(triangle: SliceLikeCategory.MorphismType) -> MorphismCategory.ObjectType:
    return triangle.first() if triangle.base_category().narrowing_base()._fixed_label == 1 else triangle.second()


# ``slice_member(t, C/x)``: ``t`` is an object of the slice or coslice: a morphism of
# ``C`` (or a generalized element denoting one) whose fixed end is ``x``, or a value
# already constructed there.
class _SliceMemberPredicate(Predicate):
    name = "slice_member"


slice_member = _SliceMemberPredicate()


def _slice_member_by_fixed_end(
    candidate: CategoryOfCategories.ElementType,
    slice_category: Category,
    assumptions: Proposition,
) -> bool | None:
    morphism = _denoted_morphism(candidate)
    if morphism in slice_category.base_of_slice().morphism_category(1):
        return sympy_ask(
            slice_category.fixed_end(morphism) == slice_category.fixed_object(),
            assumptions,
        )
    return sympy_ask(member(candidate, slice_category), assumptions)


register_handler(slice_member, _slice_member_by_fixed_end)


class SliceLikeCategory(CommaSpecialization):
    """The pullback of ``ev_k: Fun([1], C) -> C`` along ``x: * -> C``; ``k = 1`` is the slice and ``k = 0`` the coslice."""

    class ObjectType:
        """A morphism of ``C`` with one endpoint pinned at ``x``: the arrow is its whole content."""

        def __repr__(self) -> str:
            return f"{self.arrow()!r} in {self.category()!r}"

    class ElementType:
        """A generalized element of such an object."""

    class MorphismType:
        """A triangle: the morphism of ``C`` between the varying objects, commuting with the two pinned arrows."""

        def __repr__(self) -> str:
            return f"{_varying_of(self)!r} in {self.category()!r}"

    def __init__(self, base: Category, fixed: CategoryOfCategories.ElementType, fixed_label: int) -> None:
        self._base_of_slice = base
        self._fixed = fixed
        self._fixed_label = fixed_label
        self._properties: MonoDict = MonoDict()
        # A functor out of this category exists only once this category does, and
        # ``structure_functors`` runs inside that construction, so both projections are
        # built there and retained (``cat/points.py`` makes the same call at the same
        # point).
        self._arrow_projection: Functor | None = None
        self._varying_projection: Functor | None = None
        point, identity = base.point_functor(fixed), Fun(base, base).one()
        super().__init__(identity if fixed_label == 1 else point, point if fixed_label == 1 else identity)
        self.retain_lifts()

    # -- the two retained projections (POL-FUN-031) ------------------------------------

    def arrows(self) -> Category:
        """``Fun([1], C)``, the category this one is a pullback of an evaluation of."""
        return Fun(_walking_arrow(), self._base_of_slice)

    def fixed_evaluation(self) -> Functor:
        """``ev_k: Fun([1], C) -> C``, the leg of the cospan this category is the pullback of."""
        return self.arrows().evaluation(_walking_arrow()(self._fixed_label))

    def defining_arrow(self) -> Functor:
        """The retained pullback projection to ``Fun([1], C)``: the defining morphism of an object, the commuting square of a triangle (POL-CAT-092)."""
        if self._arrow_projection is None:
            self._arrow_projection = Cat().construct_morphism(self, self.arrows(), _structure_of, self._square)
        return self._arrow_projection

    def fixed_projection(self) -> Functor:
        """Return the retained projection from the slice to its varying objects in ``C``."""
        if self._varying_projection is None:
            self._varying_projection = Cat().construct_morphism(
                self,
                self._base_of_slice,
                lambda member_object: self.varying_end(self.defining_arrow_of(member_object)),
                lambda triangle: _varying_of(triangle),
            )
        return self._varying_projection

    def structure_functors(self) -> tuple[Functor, ...]:
        """The fixed projection: a slice inherits the methods of the category its objects sit over (POL-CAT-047, POL-FUN-031)."""
        return (*super().structure_functors(), self.fixed_projection())

    def retain_lifts(self) -> None:
        """Retain on the fixed projection the lifts that make it a discrete fibration over ``x`` and a discrete opfibration under it (POL-FUN-031)."""
        if self._fixed_label == 1:
            self.fixed_projection().retain_cartesian_lifts(self._lift)
            return
        self.fixed_projection().retain_cocartesian_lifts(self._lift)

    def _lift(
        self,
        morphism: MorphismCategory.ObjectType,
        member_object: SliceLikeCategory.ObjectType,
    ) -> SliceLikeCategory.MorphismType:
        """The lift of ``f: y -> z`` at an object of the fibre: ``f: (p * f) -> p`` over ``x``, ``f: p -> (f * p)`` under it."""
        structure = self.defining_arrow_of(member_object)
        if self._fixed_label == 1:
            assert morphism.codomain() is structure.domain(), f"{morphism!r} does not end at the varying object of {member_object!r}"
            return self.construct_morphism(self(structure * morphism), member_object, morphism)
        assert morphism.domain() is structure.codomain(), f"{morphism!r} does not start at the varying object of {member_object!r}"
        return self.construct_morphism(member_object, self(morphism * structure), morphism)

    # -- the category's own data -------------------------------------------------------

    def base_of_slice(self) -> Category:
        return self._base_of_slice

    def fixed_object(self) -> CategoryOfCategories.ElementType:
        return self._fixed

    def fixed_end(self, morphism: MorphismCategory.ObjectType) -> CategoryOfCategories.ElementType:
        """The end of a morphism of ``C`` that an object must fix: the codomain over ``x``, the domain under ``x``."""
        if self._fixed_label == 1:
            return morphism.codomain()
        return morphism.domain()

    def varying_end(self, morphism: MorphismCategory.ObjectType) -> CategoryOfCategories.ElementType:
        """The other end: the domain over ``x``, the codomain under ``x``."""
        if self._fixed_label == 1:
            return morphism.domain()
        return morphism.codomain()

    def defining_arrow_of(self, candidate: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        """The defining morphism of a slice object, of a morphism of ``C``, or of a generalized element denoting one."""
        morphism = _denoted_morphism(candidate)
        if morphism in self._base_of_slice.morphism_category(1):
            return morphism
        return self.defining_arrow().on_object(candidate)

    def property_type(self, property_category: Category) -> type[SliceProperty]:
        """The base category supplies its subobject realization (POL-CAT-092)."""
        monomorphisms = self._base_of_slice.morphism_category(1).Monomorphisms()
        if self._fixed_label == 1 and property_category is monomorphisms:
            return self._base_of_slice.subobjects_type()
        return SliceProperty

    def _property(self, property_category: Category) -> Category:
        """The pullback of a property subcategory of ``Mor(C)`` along the defining-arrow functor, retained per property."""
        if property_category not in self._properties:
            family = self.property_type(property_category)(self, property_category)
            if (
                self._fixed_label == 1
                and property_category is self._base_of_slice.morphism_category(1).Monomorphisms()
                and self._fixed in self._base_of_slice.Products()
            ):
                family._product_subobjects = SubobjectsOfProduct(family, property_category)
            self._properties[property_category] = family
        return self._properties[property_category]

    def Monomorphisms(self) -> Category:
        return self._property(self._base_of_slice.morphism_category(1).Monomorphisms())

    def Epimorphisms(self) -> Category:
        return self._property(self._base_of_slice.morphism_category(1).Epimorphisms())

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return slice_member(candidate, self)

    # -- construction ------------------------------------------------------------------

    def __call__(self, value: CategoryOfCategories.ElementType) -> SliceLikeCategory.ObjectType:
        """The object of a morphism ``t`` of ``C`` whose fixed end is ``x``, or of a generalized element denoting one."""
        if is_placed(value, self):
            return value
        morphism = _denoted_morphism(value)
        if morphism not in self._base_of_slice.morphism_category(1) and value in self.arrows():
            morphism = self.arrows().diagram(value).on_morphism(_walking_arrow().generator("0->1"))
        assert morphism in self._base_of_slice.morphism_category(1), f"{value!r} denotes no morphism of {self._base_of_slice!r}"
        assert ask(self.fixed_end(morphism) == self._fixed) is not False, f"{morphism!r} does not end at {self._fixed!r}"
        varying = self.varying_end(morphism)
        return self.from_arrow(varying if self._fixed_label == 1 else _star(), _star() if self._fixed_label == 1 else varying, morphism)

    def construct_morphism(self, domain: SliceLikeCategory.ObjectType, codomain: SliceLikeCategory.ObjectType, varying: MorphismCategory.ObjectType) -> SliceLikeCategory.MorphismType:
        return self.morphism_from_pair(domain, codomain, varying if self._fixed_label == 1 else _star_identity(), _star_identity() if self._fixed_label == 1 else varying)

    def _square(self, triangle: SliceLikeCategory.MorphismType) -> NaturalTransformation:
        return self.arrow_projection().on_morphism(triangle)

    def varying_component(self, square: NaturalTransformation) -> MorphismCategory.ObjectType:
        """The component of a commuting square of ``Fun([1], C)`` at the varying end: the triangle it is."""
        return square.component(_walking_arrow()(1 - self._fixed_label))

    def __repr__(self) -> str:
        if self._fixed_label == 1:
            return f"{self._base_of_slice!r}.SliceOver({self._fixed!r})"
        return f"{self._base_of_slice!r}.CosliceUnder({self._fixed!r})"


def _chosen_pullback(apex: SliceLikeCategory) -> SliceLikeCategory:
    """Place a slice or coslice in ``Cat().Pullbacks()`` with the universal data of its square (POL-MATH-037).

    The cospan is ``ev_k: Fun([1], C) -> C`` and ``x: * -> C``; the cone legs are the two
    retained projections and, at the shared vertex, the constant functor at ``x``.  The
    mediator of a cone ``(u: T -> Fun([1], C), T -> 1)`` sends ``t`` to the object of the
    arrow ``u(t)``, whose fixed end the cone's own commutation pins at ``x``.
    """
    evaluation = apex.fixed_evaluation()
    diagram = cospan_diagram(Cat(), evaluation, apex.base_of_slice().point_functor(apex.fixed_object()))
    cospan = Cat().WalkingCospan()
    to_point = Cat().construct_morphism(apex, Cat().Terminal(), lambda member_object: _star(), lambda triangle: _star_identity())
    legs = {0: apex.defining_arrow(), 1: to_point, 2: evaluation * apex.defining_arrow()}

    def mediator(candidate_cone: NaturalTransformation) -> Functor:
        to_arrows = candidate_cone.component(cospan(0))
        return Fun(to_arrows.domain(), apex)(
            lambda member_object: apex(to_arrows.on_object(member_object)),
            lambda morphism: apex.construct_morphism(
                apex(to_arrows.on_object(morphism.domain())),
                apex(to_arrows.on_object(morphism.codomain())),
                apex.varying_component(to_arrows.on_morphism(morphism)),
            ),
        )

    return Cat().Pullbacks().with_universal_data(diagram, apex, cone(diagram, apex, lambda vertex: legs[cospan.label(vertex)]), mediator)


def slice_over(base: Category, fixed: CategoryOfCategories.ElementType) -> SliceLikeCategory:
    """``C.SliceOver(x)``: the chosen pullback of ``ev_1`` along ``x``, retained in ``Cat().Pullbacks()``."""
    return _chosen_pullback(SliceLikeCategory(base, fixed, 1))


def coslice_under(base: Category, fixed: CategoryOfCategories.ElementType) -> SliceLikeCategory:
    """``C.CosliceUnder(x)``: the chosen pullback of ``ev_0`` along ``x``, retained in ``Cat().Pullbacks()``."""
    return _chosen_pullback(SliceLikeCategory(base, fixed, 0))


# -- comma categories ------------------------------------------------------------------------


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


def comma_category(first: Functor, second: Functor) -> CommaCategory:
    """The comma category ``(F, G)``: the pullback of ``(ev_0, ev_1)`` along ``F * G``, retained per pair; objects ``((a, b), f: F a -> G b)``."""
    return Cat().Comma(first, second)


def _construct_comma_category(
    first: Functor,
    second: Functor,
    category_type: type[CommaCategory] = CommaCategory,
) -> CommaCategory:
    result = comma_objects(first, second) if category_type is CommaCategory else category_type(first, second)
    diagram = cospan_diagram(Cat(), _pair_functor(first, second), _endpoint_functor(first.codomain()))
    pairs, arrows = result.pair_projection(), result.arrow_projection()
    legs = (pairs, arrows, diagram.on_morphism(diagram.domain().generator("0->2")) * pairs)

    def mediator(candidate: NaturalTransformation) -> Functor:
        pair, arrow = candidate.component(diagram.domain()(0)), candidate.component(diagram.domain()(1))
        def on_object(value: CategoryOfCategories.ElementType) -> CommaCategory.ObjectType:
            components = pair.on_object(value)
            image = arrow.on_object(value)
            defining = arrow.codomain().diagram(image).on_morphism(_walking_arrow().generator("0->1"))
            return result.from_arrow(components.family_component(0), components.family_component(1), defining)
        return Fun(pair.domain(), result)(on_object, lambda morphism: result.morphism_from_pair(
            on_object(morphism.domain()), on_object(morphism.codomain()),
            pair.on_morphism(morphism).family_component(0), pair.on_morphism(morphism).family_component(1)))

    return Cat().Pullbacks().with_universal_data(diagram, result, cone(diagram, result, lambda vertex: legs[diagram.domain().label(vertex)]), mediator)


# -- the fixed-object construction categories (POL-CAT-092/094, POL-CAT-026, POL-FUN-013) ----

# ``has_morphism_property(x, S)``: the defining arrow of ``x`` is an object of the
# property subcategory of ``Mor(C)`` that ``S`` pulls back.
class _HasMorphismPropertyPredicate(Predicate):
    name = "has_morphism_property"


has_morphism_property = _HasMorphismPropertyPredicate()


def _has_morphism_property(
    candidate: CategoryOfCategories.ElementType,
    family: Category,
    assumptions: Proposition,
) -> bool | None:
    """The containment question the property subcategory declares, asked of the defining arrow (POL-CAT-043, POL-CAT-044)."""
    return sympy_ask(
        family.property_category().membership_proposition(family.defining_arrow_of(candidate)),
        assumptions,
    )


register_handler(has_morphism_property, _has_morphism_property)


class SliceProperty(FullSubcategory[[MorphismCategory.ObjectType], []]):
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
    class ObjectType:
        """An object of the slice whose defining arrow has the property, as the same value."""

    class ElementType:
        """A point of such an object."""

    class MorphismType:
        """A triangle of the slice between two such objects."""

    def __init__(self, ambient: SliceLikeCategory | SliceProperty, property_category: Category) -> None:
        self._property_category = property_category
        self._retained: MonoDict = MonoDict()
        self._product_subobjects: SubobjectsOfProduct | None = None
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

    def defining_arrow_of(self, candidate: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        return self._ambient.defining_arrow_of(candidate)

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return self._ambient.membership_proposition(candidate) & has_morphism_property(candidate, self)

    def __call__(self, value: CategoryOfCategories.ElementType) -> SliceLikeCategory.ObjectType:
        """The object of a morphism with the property: the trusted constructor of the property on it (POL-MATH-037), rejected only when decided false."""
        assert ask(has_morphism_property(value, self)) is not False, f"{value!r} is not in {self._property_category!r}"
        refine(self.defining_arrow_of(value), self._property_category)
        member_object = self._ambient(value)
        refine(member_object, self)
        if self._product_subobjects is not None:
            refine(member_object, self._product_subobjects)
        return member_object

    def __repr__(self) -> str:
        return f"{self._ambient!r}.{self._property_category.name()}()"


class SubobjectsOfProduct(SliceProperty):
    """``C.Subobjects(P)`` for a product ``P``: the subobjects that read ``P``'s components through their own monomorphism.

    The fixed slice selects this specialization of its base subobject realization
    when its fixed object is a product (POL-CAT-094, POL-KERNEL-025).
    """

    # The product structure of ``P`` adds no point and no triangle; it adds
    # ``product_projection`` on the subobject below.
    class ElementType:
        """A point of a subobject of a product."""

    class MorphismType:
        """A triangle of the slice between two subobjects of a product."""

    class ObjectType:
        """A subobject ``j: S -> P`` of a product: its components are ``P``'s projections after ``j``."""

        def product_projection(
            self,
            index: CategoryOfCategories.ElementType | Hashable,
        ) -> MorphismCategory.ObjectType:
            """``P.product_projection(i) after j``, so a subobject of a product has every component (POL-CAT-094)."""
            monomorphism = self.category().narrowing_base().defining_arrow_of(self)
            return monomorphism.codomain().product_projection(index) * monomorphism
