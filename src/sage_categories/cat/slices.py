"""Slices, coslices, and comma categories as strict pullbacks; their fibration lifts; the subobject families (POL-CAT-026/095, POL-FUN-013/031, POL-SCOPE-003).

``C.SliceOver(x)`` is the strict pullback in ``Cat()`` of ``ev_1: Fun([1], C) -> C``
along the point ``x: 1 -> C``, and ``C.CosliceUnder(x)`` the pullback of ``ev_0``
(``specs/functor.md``, "Slices and coslices").  It is the category where its own
constructor and its own API live: it writes its three declarations, supplies the
universal data of that pullback square, and states which of its retained projections
supplies inherited implementation (POL-CAT-057, POL-MATH-037).

An object is the morphism of ``C`` with the pinned endpoint; a morphism is the
morphism of ``C`` between the varying objects.  The retained projections are

- ``defining_arrow(): C.SliceOver(x) -> Fun([1], C)``, returning that morphism and,
  on a triangle, its commuting square;
- ``fixed_projection(): C.SliceOver(x) -> C``, the composite with ``ev_0`` (with
  ``ev_1`` for the coslice), returning the varying object and the varying morphism.

``fixed_projection()`` is the one selected structure functor.  A slice inherits the
methods of the category its objects sit over, so its objects reach ``C.ObjectType``
and its triangles ``C.MorphismType`` through the ordinary compiler mechanism
(POL-CAT-047, POL-CAT-053, POL-KERNEL-028/029).  Selection asserts no subcategory
relation: an object over ``x`` is a pair, and the Python inheritance states only that
the methods of ``C`` apply to its varying object (D05, D07).

The fixed slice projection is the category of elements of ``Mor(C)(-, x)`` and a
discrete fibration for every ``C``: the cartesian lift of ``f: y -> z`` at ``(z, p)``
is ``f: (y, p * f) -> (z, p)`` by precomposition (nLab "discrete fibration", inspected
2026-08-27: "the representable presheaf on an object X corresponds to the canonical
functor B/X -> B from the slice category over X").  Dually the coslice projection is a
discrete opfibration with cocartesian lifts by postcomposition.  Each slice registers
its lift rule on its fixed projection, which retains the lifts
(``Functor.cartesian_lift``); the evaluations ``ev_1`` and ``ev_0`` retain their own
lifts (``cat/diagrams.py``), so the total category and its fiber carry distinct lift
data (POL-FUN-031).

A comma category ``(F, G)`` for ``F: A -> C`` and ``G: B -> C`` is the pullback of
``(ev_0, ev_1): Fun([1], C) -> C * C`` along ``F * G`` (Mathlib
``CategoryTheory.Comma``: objects are triples ``(left, right, hom: L left -> R right)``
and morphisms are commuting squares; inspected 2026-08-27), constructed by the owned
pullback of categories.

Objects of ``C.SliceOver(x)`` are the generalized elements of ``x``
(``specs/functor.md``, "Slices and coslices"; AGENTS.md, "Core categorical
architecture"): a morphism ``t: T -> x`` or an element with that defining morphism is
accepted as an object, and is a member by the same decision.

``C.Subobjects(x)`` is ``C.SliceOver(x).Monomorphisms()``: the property subcategory
``Mor(C).Monomorphisms()`` pulled back along the retained defining-arrow functor of the
slice (POL-CAT-092, POL-FUN-013/014).  A full subcategory is identity on values, so that
pullback is the full subcategory of the slice on the objects whose defining arrow has the
property (``specs/functor.md``, "Fixed-object construction categories"), and
``SliceProperty`` retains both projections of the square.  Whether an arrow has the
property is the containment question ``Mor(C).Monomorphisms()`` declares, asked of that
arrow; nothing here reaches for that category's predicate object (POL-CAT-043,
POL-CAT-044).  ``C.CoveringObjects(y)`` uses epimorphisms: a covering object of ``y`` is
the pair ``(X, p: X -> y)``, not ``p`` alone (POL-CAT-026).  ``C.Superobjects(x)`` and
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
from dataclasses import dataclass

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.constructions import cone
from sage_categories.cat.diagrams import cospan_diagram, sequence_position
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.properties import FullSubcategory
from sage_categories.kernel import compiler
from sage_categories.kernel.construction import MorphismConstructionInput, ObjectConstructionInput
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of
from sage_categories.kernel.transport import construction_input

__all__ = [
    "SliceLikeCategory",
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
    """``1_*``: the unit of ``End_1(*)``, the image of every triangle under the projection to ``1`` (POL-CAT-023)."""
    star = _star()
    return star.category().morphism_category(1)(star, star).one()


def _denoted_morphism(candidate: CategoryPoint) -> CategoryPoint:
    """The morphism a candidate denotes: the defining morphism of a generalized element, else the candidate itself."""
    if role_of(candidate) is Role.ELEMENT:
        return candidate.defining_morphism()
    return candidate


@dataclass(frozen=True, eq=False, slots=True)
class SliceObjectData:
    """The local state introduced by an object of a slice or coslice: the morphism of ``C`` whose fixed end is ``x``."""

    structure: MorphismOfCategory


@dataclass(frozen=True, eq=False, slots=True)
class SliceTriangleData:
    """The local state introduced by a morphism of a slice or coslice: the morphism of ``C`` between the varying objects."""

    varying: MorphismOfCategory


def _structure_of(member_object: SliceLikeCategory.ObjectType) -> MorphismOfCategory:
    """The defining arrow of an object of a slice or coslice: the state its declaration below introduces."""
    return member_object._structure


def _varying_of(triangle: SliceLikeCategory.MorphismType) -> MorphismOfCategory:
    """The morphism of ``C`` a triangle is: the state its declaration below introduces."""
    return triangle._varying


# ``slice_member(t, C/x)``: ``t`` is an object of the slice or coslice: a morphism of
# ``C`` (or a generalized element denoting one) whose fixed end is ``x``, or a value
# already constructed there.
slice_member = Predicate("slice_member", 2, False)


def _slice_member_by_fixed_end(candidate: CategoryPoint, slice_category: Category) -> Decision:
    morphism = _denoted_morphism(candidate)
    if morphism in slice_category.base_of_slice().morphism_category(1):
        return ask(slice_category.fixed_end(morphism) == slice_category.fixed_object())
    return ask(member(candidate, slice_category))


slice_member.register_handler(_slice_member_by_fixed_end)


class SliceLikeCategory(Category[[MorphismOfCategory], []]):
    """The pullback of an evaluation ``ev_k: Fun([1], C) -> C`` along ``x: 1 -> C``; ``k = 1`` is the slice, ``k = 0`` the coslice."""

    class ObjectType(ObjectOfCategory):
        """A morphism of ``C`` with one endpoint pinned at ``x``: the arrow is its whole content."""

        def __init__(self, data: SliceObjectData) -> None:
            self._structure = data.structure
            super().__init__()

        def __repr__(self) -> str:
            return f"{self._structure!r} in {self.category()!r}"

    class ElementType(ElementOfObject):
        """A generalized element of such an object."""

    class MorphismType(MorphismOfCategory):
        """A triangle: the morphism of ``C`` between the varying objects, commuting with the two pinned arrows."""

        def __init__(self, data: SliceTriangleData) -> None:
            self._varying = data.varying
            super().__init__()

        def __repr__(self) -> str:
            return f"{self._varying!r} in {self.category()!r}"

    def __init__(self, base: Category, fixed: ObjectOfCategory, fixed_label: int) -> None:
        self._base_of_slice = base
        self._fixed = fixed
        self._fixed_label = fixed_label
        self._objects: MonoDict = MonoDict()
        self._properties: MonoDict = MonoDict()
        self._retained: MonoDict = MonoDict()
        # A functor out of this category exists only once this category does, and
        # ``structure_functors`` runs inside that construction, so both projections are
        # built there and retained (``cat/points.py`` makes the same call at the same
        # point).
        self._arrow_projection: Functor | None = None
        self._varying_projection: Functor | None = None
        super().__init__()
        self._equality.register_handler(self._equal)
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
        """``C/x -> C``: the evaluation at the varying end after the projection to the arrows, retained once.

        Its images are values that the defining data of a slice object already names --
        the varying object of the arrow, and the varying morphism of a triangle -- so it
        has no value-level action of its own and states the two construction-input
        conversions instead.  The kernel builds its public images and the inherited state
        from those (POL-FUN-035, POL-KERNEL-029).
        """
        if self._varying_projection is None:
            projection = Cat().construct_morphism(self, self._base_of_slice, None, None)
            projection.retain_object_constructor_conversion(self._varying_object_input)
            projection.retain_morphism_constructor_conversion(self._varying_morphism_input)
            self._varying_projection = projection
        return self._varying_projection

    def _varying_object_input[Datum](self, source: ObjectConstructionInput[ObjectOfCategory, SliceObjectData]) -> ObjectConstructionInput[ObjectOfCategory, Datum]:
        """The input of the varying object of a slice object: that of an object of ``C`` already constructed."""
        return construction_input(self.varying_end(source.datum.structure), compiler.node(self._base_of_slice, Role.OBJECT))

    def _varying_morphism_input[Datum](self, source: MorphismConstructionInput[MorphismOfCategory, SliceTriangleData]) -> MorphismConstructionInput[MorphismOfCategory, Datum]:
        """The input of the varying morphism of a triangle: that of a morphism of ``C`` already constructed."""
        return construction_input(source.datum.varying, compiler.node(self._base_of_slice, Role.MORPHISM))

    def structure_functors(self) -> tuple[Functor, ...]:
        """The fixed projection: a slice inherits the methods of the category its objects sit over (POL-CAT-047, POL-FUN-031)."""
        return (self.fixed_projection(),)

    def retain_lifts(self) -> None:
        """Retain on the fixed projection the lifts that make it a discrete fibration over ``x`` and a discrete opfibration under it (POL-FUN-031)."""
        if self._fixed_label == 1:
            self.fixed_projection().retain_cartesian_lifts(self._lift)
            return
        self.fixed_projection().retain_cocartesian_lifts(self._lift)

    def _lift(self, morphism: MorphismOfCategory, member_object: SliceLikeCategory.ObjectType) -> SliceLikeCategory.MorphismType:
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

    def fixed_object(self) -> ObjectOfCategory:
        return self._fixed

    def fixed_end(self, morphism: MorphismOfCategory) -> ObjectOfCategory:
        """The end of a morphism of ``C`` that an object must fix: the codomain over ``x``, the domain under ``x``."""
        if self._fixed_label == 1:
            return morphism.codomain()
        return morphism.domain()

    def varying_end(self, morphism: MorphismOfCategory) -> ObjectOfCategory:
        """The other end: the domain over ``x``, the codomain under ``x``."""
        if self._fixed_label == 1:
            return morphism.domain()
        return morphism.codomain()

    def defining_arrow_of(self, candidate: CategoryPoint) -> MorphismOfCategory:
        """The defining morphism of a slice object, of a morphism of ``C``, or of a generalized element denoting one."""
        morphism = _denoted_morphism(candidate)
        if morphism in self._base_of_slice.morphism_category(1):
            return morphism
        return self.defining_arrow().on_object(candidate)

    def property_type(self, property_category: Category) -> type[SliceProperty]:
        """The subobjects of a product state their components; every other property subcategory of a slice has no such method (POL-CAT-094)."""
        monomorphisms = self._base_of_slice.morphism_category(1).Monomorphisms()
        if self._fixed_label == 1 and property_category is monomorphisms and self._fixed in self._base_of_slice.Products():
            return SubobjectsOfProduct
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

    def _equal(self, first: CategoryPoint, candidate: object) -> Decision:
        """Two objects are equal when their defining arrows are, two triangles when their varying morphisms are."""
        if first in self and candidate in self:
            return ask(self.defining_arrow_of(first) == self.defining_arrow_of(candidate))
        triangles = self.morphism_category(1)
        if first in triangles and candidate in triangles:
            return ask(_varying_of(first) == _varying_of(candidate))
        return Unknown

    # -- construction ------------------------------------------------------------------

    def __call__(self, value: CategoryPoint) -> SliceLikeCategory.ObjectType:
        """The object of a morphism ``t`` of ``C`` whose fixed end is ``x``, or of a generalized element denoting one."""
        if is_placed(value, self):
            return value
        morphism = _denoted_morphism(value)
        assert morphism in self._base_of_slice.morphism_category(1), f"{value!r} denotes no morphism of {self._base_of_slice!r}"
        assert ask(self.fixed_end(morphism) == self._fixed) is not False, f"{morphism!r} does not end at {self._fixed!r}"
        if morphism not in self._objects:
            self._objects[morphism] = self.ObjectType(category=self, data=SliceObjectData(morphism))
        return self._objects[morphism]

    def construct_morphism(self, domain: SliceLikeCategory.ObjectType, codomain: SliceLikeCategory.ObjectType, varying: MorphismOfCategory) -> SliceLikeCategory.MorphismType:
        """The triangle whose varying morphism is ``varying``, which must commute with the two defining arrows."""
        source, target = self.defining_arrow_of(domain), self.defining_arrow_of(codomain)
        assert varying in self._base_of_slice.morphism_category(1)(self.varying_end(source), self.varying_end(target))
        assert ask(self._commutes(source, target, varying)) is not False, f"{varying!r} does not commute with {source!r} and {target!r}"
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=domain,
            codomain=codomain,
            data=SliceTriangleData(varying),
        )

    def _commutes(self, source: MorphismOfCategory, target: MorphismOfCategory, varying: MorphismOfCategory) -> Proposition:
        """The commuting condition of a triangle: ``target . varying == source`` over ``x``, ``varying . source == target`` under it."""
        if self._fixed_label == 1:
            return target * varying == source
        return varying * source == target

    def construct_identity(self, member_object: SliceLikeCategory.ObjectType) -> SliceLikeCategory.MorphismType:
        varying = self.varying_end(self.defining_arrow_of(member_object))
        return self.construct_morphism(member_object, member_object, varying.category().morphism_category(1)(varying, varying).one())

    def composite(self, second: SliceLikeCategory.MorphismType, first: SliceLikeCategory.MorphismType) -> SliceLikeCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.construct_morphism(first.domain(), second.codomain(), _varying_of(second) * _varying_of(first))

    def _square(self, triangle: SliceLikeCategory.MorphismType) -> NaturalTransformation:
        """The commuting square in ``Fun([1], C)`` of a triangle: the varying morphism, with the identity of ``x`` at the fixed end."""
        fixed = self._fixed
        components = {
            self._fixed_label: fixed.category().morphism_category(1)(fixed, fixed).one(),
            1 - self._fixed_label: _varying_of(triangle),
        }
        source, target = self.defining_arrow_of(triangle.domain()), self.defining_arrow_of(triangle.codomain())
        return self.arrows().morphism_category(1)(source, target)(lambda vertex: components[_walking_arrow().label(vertex)])

    def varying_component(self, square: NaturalTransformation) -> MorphismOfCategory:
        """The component of a commuting square of ``Fun([1], C)`` at the varying end: the triangle it is."""
        return square.component(_walking_arrow()(1 - self._fixed_label))

    def __repr__(self) -> str:
        if self._fixed_label == 1:
            return f"{self._base_of_slice!r}.SliceOver({self._fixed!r})"
        return f"{self._base_of_slice!r}.CosliceUnder({self._fixed!r})"


def _chosen_pullback(apex: SliceLikeCategory) -> SliceLikeCategory:
    """Place a slice or coslice in ``Cat().Pullbacks()`` with the universal data of its square (POL-MATH-037).

    The cospan is ``ev_k: Fun([1], C) -> C`` and ``x: 1 -> C``; the cone legs are the two
    retained projections and, at the shared vertex, the constant functor at ``x``.  The
    mediator of a cone ``(u: T -> Fun([1], C), T -> 1)`` sends ``t`` to the object of the
    arrow ``u(t)``, whose fixed end the cone's own commutation pins at ``x``.
    """
    evaluation = apex.fixed_evaluation()
    diagram = cospan_diagram(Cat(), evaluation, apex.base_of_slice().point_functor(apex.fixed_object()))
    cospan = Cat().Horn(2, 2)
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


def slice_over(base: Category, fixed: ObjectOfCategory) -> SliceLikeCategory:
    """``C.SliceOver(x)``: the chosen pullback of ``ev_1`` along ``x``, retained in ``Cat().Pullbacks()``."""
    return _chosen_pullback(SliceLikeCategory(base, fixed, 1))


def coslice_under(base: Category, fixed: ObjectOfCategory) -> SliceLikeCategory:
    """``C.CosliceUnder(x)``: the chosen pullback of ``ev_0`` along ``x``, retained in ``Cat().Pullbacks()``."""
    return _chosen_pullback(SliceLikeCategory(base, fixed, 0))


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


def comma_category(first: Functor, second: Functor) -> Category:
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


class SliceProperty(FullSubcategory[[MorphismOfCategory], []]):
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
    class ObjectType(ObjectOfCategory):
        """An object of the slice whose defining arrow has the property, as the same value."""

    class ElementType(ElementOfObject):
        """A point of such an object."""

    class MorphismType(MorphismOfCategory):
        """A triangle of the slice between two such objects."""

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

    def __call__(self, value: CategoryPoint) -> SliceLikeCategory.ObjectType:
        """The object of a morphism with the property: the trusted constructor of the property on it (POL-MATH-037), rejected only when decided false."""
        assert ask(has_morphism_property(value, self)) is not False, f"{value!r} is not in {self._property_category!r}"
        self._property_category(self.defining_arrow_of(value))
        member_object = self._ambient(value)
        refine(member_object, self)
        return member_object

    def __repr__(self) -> str:
        return f"{self._ambient!r}.{self._property_category.name()}()"


class SubobjectsOfProduct(SliceProperty):
    """``C.Subobjects(P)`` for a product ``P``: the subobjects that read ``P``'s components through their own monomorphism.

    ``SliceLikeCategory.property_type`` names this class exactly when the fixed object is a
    product, so the method belongs to the subobjects of a product and to no other
    subobject (POL-CAT-094, POL-KERNEL-025).
    """

    # The product structure of ``P`` adds no point and no triangle; it adds
    # ``product_projection`` on the subobject below.
    class ElementType(ElementOfObject):
        """A point of a subobject of a product."""

    class MorphismType(MorphismOfCategory):
        """A triangle of the slice between two subobjects of a product."""

    class ObjectType(ObjectOfCategory):
        """A subobject ``j: S -> P`` of a product: its components are ``P``'s projections after ``j``."""

        def product_projection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """``P.product_projection(i) after j``, so a subobject of a product has every component (POL-CAT-094)."""
            monomorphism = self.category().narrowing_base().defining_arrow_of(self)
            return monomorphism.codomain().product_projection(index) * monomorphism
