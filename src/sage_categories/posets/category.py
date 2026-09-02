"""Implement partially ordered sets, monotone maps, and their named projection to sets."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from sage.misc.cachefunc import cached_method
from sage.rings.integer import Integer
from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category
from sage_categories.cat.constructions import cone
from sage_categories.cat.diagrams import sequence_position
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.shapes import ThinCategory
from sage_categories.cat.predicates import AppliedPredicate, Predicate, Proposition, ask, conjunction, disjunction, implication, negation, predicate, register_handler
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.roles import Role, role_of
from sage_categories.sets.category import Sets
from sage_categories.sets.elements import Datum, SetElement
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import MembershipRule, SetObject

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

from sage_categories.sets.category import SetMap

__all__ = [
    "FinitePosets",
    "FiniteTotallyOrderedSets",
    "MonotoneMap",
    "Poset",
    "PosetElement",
    "Posets",
    "PosetsCategory",
    "SimplexOrders",
    "Thin",
    "TotallyOrderedSets",
    "covers",
    "order_preserving",
    "partial_order",
]

# ``partial_order(R)``: the relation ``R`` on ``X`` is reflexive, antisymmetric, and transitive.
partial_order: Predicate = predicate("partial_order")
# ``order_preserving(P, Q, f)``: the set map ``f: U(P) -> U(Q)`` is monotone.
order_preserving: Predicate = predicate("order_preserving")

# ``covers(P, x, y)``: y covers x in the poset P.
covers: Predicate = predicate("covers")

type Relation = dict[tuple[int, int], Decision]


@dataclass(eq=False, slots=True)
class PosetObjectData:
    """The private state introduced by a partial order."""

    relation: SetObject
    elements: MonoDict = field(default_factory=MonoDict)


@dataclass(frozen=True, eq=False, slots=True)
class PosetMorphismData:
    """The construction datum of a monotone map: the set map it is (``specs/ordered-sets.md``)."""

    set_map: SetMap


class PosetDeclaration:
    """The local ``Posets().ObjectType`` declaration."""

    def __init__(self, data: PosetObjectData) -> None:
        self._poset_object_data = data
        super().__init__()

    def relation(self) -> SetObject:
        """The defining order relation ``R``, a chosen subset of ``X * X``."""
        return self._poset_object_data.relation

    def carrier(self) -> SetObject:
        """The underlying set ``U(P)``."""
        return Posets().underlying_set_functor().on_object(self)

    def element(self, point: SetElement) -> PosetElement:
        """The point over a point ``x: * -> U(P)``: the monotone map ``* -> P`` under ``x``."""
        state = self._poset_object_data
        carrier = self.carrier()
        assert point in carrier, f"{point!r} is not a point of {carrier!r}"
        if point not in state.elements:
            # The point of ``P`` is a morphism of the category ``P`` was
            # placed in, not of ``Posets()``: a functor out of ``Posets().Finite()``
            # transports a morphism of ``Mor(Posets().Finite())`` (POL-CAT-074).
            posets, category = Posets(), self.category()
            defining_morphism = posets._construct_morphism(posets.Terminal(), self, point.defining_morphism())
            refine(defining_morphism, category.morphism_category(1))
            state.elements[point] = category.element_from_defining_morphism(defining_morphism)
        return state.elements[point]

    def sub_poset_inclusion(self, predicate: MembershipRule) -> MonotoneMap:
        """The inclusion monomorphism of the sub-poset ``{x in P : predicate(x)}`` into ``P``."""
        subset = self.carrier().subset_from(predicate)
        return Posets().underlying_set_functor().cartesian_lift(subset.monomorphism(), self)

    def sub_poset(self, predicate: MembershipRule) -> Poset:
        """The sub-poset ``{x in P : predicate(x)}`` with the induced order (POL-LEAF-029/030)."""
        return self.sub_poset_inclusion(predicate).domain()

    def covers(self, lower: PosetElement, upper: PosetElement) -> AppliedPredicate:
        """Applied proposition for the cover relation ``lower < upper`` with no element strictly between."""
        return covers(self, lower, upper)

    def __mul__(self, other: Poset) -> Poset:
        """The binary product poset with coordinatewise partial order."""
        return Posets().binary_product(self, other)

    def is_total(self) -> AppliedPredicate:
        """Totality: any two elements are comparable."""
        return Posets().TotallyOrdered().predicate()(self)

    @cached_method
    def thin_category(self) -> ThinCategory:
        """The thin category whose objects are the points of this poset (POL-CAT-070)."""
        from sage_categories.cat.shapes import ThinCategory

        carrier = self.carrier()
        order = predicate(f"ThinOrder({self!r})")

        def _thin_le(left: CategoryOfCategories.ElementType, right: CategoryOfCategories.ElementType, assumptions: Proposition) -> Decision:
            return ask(self.element(left) <= self.element(right))

        register_handler(order, _thin_le)
        return ThinCategory(carrier, order)

    def _pair(self, left: SetElement, right: SetElement) -> SetElement:
        return _pair_point(_square(self._poset_object_data.relation), left, right)

    def __repr__(self) -> str:
        return f"Poset({self.carrier()!r})"


class PosetElementDeclaration:
    """The local ``Posets().ElementType`` declaration."""

    def __le__(self, other: PosetElement) -> AppliedPredicate:
        """``x <= y``: the pair point ``(U(x), U(y))`` is a member of ``R``."""
        poset = self.parent()
        assert _is_point(self) and _is_point(other), f"{self!r} <= {other!r} compares points"
        assert other.parent() is poset, f"{other!r} is not an element of {poset!r}"
        underlying = Posets().underlying_set_functor()
        return poset.relation().membership_proposition(poset._pair(underlying.on_element(self), underlying.on_element(other)))

    def __lt__(self, other: PosetElement) -> Proposition:
        return (self <= other) & (self != other)

    def __ge__(self, other: PosetElement) -> AppliedPredicate:
        return other <= self

    def __gt__(self, other: PosetElement) -> Proposition:
        return (other <= self) & (self != other)

    def __repr__(self) -> str:
        return f"point of {self.parent()!r} with domain {self.defining_morphism().domain()!r}"


class MonotoneMapDeclaration:
    """The local monotone-map declaration; set-map state arrives through ``U``."""

    def __init__(self, data: PosetMorphismData) -> None:
        self._poset_morphism_data = data
        super().__init__()

    def set_map(self) -> SetMap:
        """The underlying set map ``U(f)``."""
        return self._poset_morphism_data.set_map

    def __call__(self, element: PosetElement) -> PosetElement:
        point = Posets().underlying_set_functor().on_element(element)
        image_point = self.set_map()(point)
        return self.codomain().element(image_point)

    def __repr__(self) -> str:
        return f"MonotoneMap({self.domain()!r} -> {self.codomain()!r})"


# -- exact handlers on finite enumerated carriers (POL-MATH-042) --------------------------


def _is_point(candidate: Any) -> bool:
    """Whether a candidate is a point of a poset.

    A classifier of the equality candidate: it
    receives exactly the second argument of ``_equal`` and must accept every input
    (POL-TYPE-004).
    """
    posets = Posets()
    return (
        role_of(candidate) is Role.ELEMENT
        and candidate.parent() in posets
        and candidate.defining_morphism().domain() is posets.Terminal()
    )


def _enumerated_points(carrier: SetObject) -> tuple[SetElement, ...]:
    assert Sets().Finite().has_chosen_enumeration(carrier)
    return tuple(carrier.point(datum) for datum in Sets().Finite().chosen_enumeration(carrier))


def _decided(decide: Callable[[SetElement, SetElement], Decision], points: tuple[SetElement, ...]) -> Relation:
    """The relation on ``points`` decided pairwise, memoized by position."""
    return {(i, j): decide(left, right) for i, left in enumerate(points) for j, right in enumerate(points)}


def _reflexive(relation: Relation, size: int) -> Decision:
    return ask(conjunction(relation[i, i] for i in range(size)))


def _antisymmetric(relation: Relation, size: int) -> Decision:
    return ask(conjunction(negation(conjunction((relation[i, j], relation[j, i]))) for i in range(size) for j in range(i + 1, size)))


def _transitive(relation: Relation, size: int) -> Decision:
    return ask(
        conjunction(
            implication(conjunction((relation[i, j], relation[j, k])), relation[i, k])
            for i in range(size)
            for j in range(size)
            for k in range(size)
        )
    )


def _total(relation: Relation, size: int) -> Decision:
    return ask(conjunction(disjunction((relation[i, j], relation[j, i])) for i in range(size) for j in range(i + 1, size)))


def _partial_order_on_enumerated(relation: CategoryOfCategories.ElementType, assumptions: Proposition) -> Decision:
    sets = Sets()
    if relation not in sets.ChosenSubsets():
        return Unknown
    square = _square(relation)
    carrier = square.product_projection(0).codomain()
    if not sets.Finite().has_chosen_enumeration(carrier):
        return Unknown
    points = _enumerated_points(carrier)
    pairs = _decided(lambda left, right: ask(relation.membership_proposition(_pair_point(square, left, right))), points)
    return ask(conjunction((_reflexive(pairs, len(points)), _antisymmetric(pairs, len(points)), _transitive(pairs, len(points)))))


def _square(relation: CategoryOfCategories.ElementType) -> SetObject:
    """The chosen product ``X * X`` that ``relation`` is a chosen subset of.

    A chosen subset retains its ambient object, which is the chosen product itself;
    that object owns the projections and the mediator (POL-CAT-046, POL-FUN-019).
    """
    square = relation.underlying_set()
    assert is_placed(square, Sets().Products()), f"{relation!r} is not a chosen subset of a chosen product"
    return square


def _pair_point(square: SetObject, left: SetElement, right: SetElement) -> SetElement:
    """The point ``(left, right): * -> X * X``."""
    from sage_categories.sets.products import Family

    index_set = Sets().Simplex(1)
    d0 = left._point_datum_() if role_of(left) is Role.ELEMENT else left
    d1 = right._point_datum_() if role_of(right) is Role.ELEMENT else right
    fam = Family(index_set, {0: d0, 1: d1}.__getitem__)
    return square.point(fam)


def _order_relation(poset: CategoryOfCategories.ElementType, points: tuple[SetElement, ...]) -> Relation:
    return _decided(lambda left, right: ask(poset.element(left) <= poset.element(right)), points)


def _total_on_enumerated(poset: CategoryOfCategories.ElementType, assumptions: Proposition) -> Decision:
    posets = Posets()
    if poset not in posets:
        return Unknown
    carrier = posets.underlying_set_functor().on_object(poset)
    if not Sets().Finite().has_chosen_enumeration(carrier):
        return Unknown
    points = _enumerated_points(carrier)
    return _total(_order_relation(poset, points), len(points))


def _order_preserving_on_enumerated(source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, set_map: CategoryOfCategories.ElementType, assumptions: Proposition) -> Decision:
    carrier = Posets().underlying_set_functor().on_object(source)
    if not Sets().Finite().has_chosen_enumeration(carrier):
        return Unknown
    points = _enumerated_points(carrier)
    images = tuple(set_map(point) for point in points)
    domain_order, codomain_order = _order_relation(source, points), _order_relation(target, images)
    return ask(
        conjunction(implication(domain_order[i, j], codomain_order[i, j]) for i in range(len(points)) for j in range(len(points)))
    )


class PosetsCategory(Category[[Rule], []]):
    """The category of partially ordered sets and monotone maps."""

    ObjectType = PosetDeclaration
    ElementType = PosetElementDeclaration
    MorphismType = MonotoneMapDeclaration

    def __init__(self) -> None:
        super().__init__()
        self.underlying_set_functor().retain_cartesian_lifts(self._induced_order)
        self._equality.register_handler(self._equal)
        self._totally_ordered = PropertySubcategory(self, "TotallyOrdered", ())
        # Handler registrations for partial_order and order_preserving are deferred
        # to module-level after _POSETS is created, so that Poset (which is defined
        # as _POSETS.ObjectType) is in the handler's __globals__ at registration time.

    # -- the selected structural functor -------------------------------------------

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.underlying_set_functor(),)

    @cached_method
    def underlying_set_functor(self) -> Functor:
        """Return ``U: Posets() -> Sets()`` on posets and monotone maps.

        A poset is constructed from its relation ``R``, and the set ``Sets()`` made from
        that construction is the common product factor of ``R``; a monotone map is constructed from its
        set map (POL-LEAF-058).
        """
        return Fun(self, Sets()).Faithful()(
            lambda order: self.carrier(order.relation()),
            lambda monotone: monotone.set_map(),
        )

    # -- construction (POL-CAT-069, POL-LEAF-002) ----------------------------------------

    def __call__(self, relation: SetObject) -> Poset:
        """``Posets()(R)``: the poset on the factor ``X`` of ``X * X`` that ``R`` is a subset of."""
        assert relation in Sets().ChosenSubsets(), f"{relation!r} is not a chosen subset"
        self.carrier(relation)
        assert ask(self.is_partial_order(relation)) is not False, f"{relation!r} is not a partial order"
        return self._construct(relation)

    def carrier(self, relation: SetObject) -> SetObject:
        """``X``: the shared factor of the chosen product ``X * X`` that the order ``R`` is a subset of."""
        square = _square(relation)
        first, second = square.product_projection(0).codomain(), square.product_projection(1).codomain()
        assert first is second, f"{relation!r} is a subset of a product of two distinct sets"
        return first

    def _construct(self, relation: SetObject) -> Poset:
        # A poset on a finite set is a finite poset by definition (POL-CAT-081).
        underlying_set = self.carrier(relation)
        poset = self.ObjectType(self, PosetObjectData(relation))
        if underlying_set in Sets().Finite():
            self.Finite()(poset)
        return poset

    def is_partial_order(self, relation: SetObject) -> AppliedPredicate:
        """The proposition that a chosen subset of ``X * X`` is reflexive, antisymmetric, and transitive."""
        return partial_order(relation)

    def is_order_preserving(self, source: Poset, target: Poset, set_map: SetMap) -> AppliedPredicate:
        """The proposition that a set map ``U(P) -> U(Q)`` is monotone."""
        return order_preserving(source, target, set_map)

    @cached_method
    def Simplex(self, dimension: int | Integer) -> Poset:
        """``[n]``: the poset on ``Sets().Simplex(n)`` with the usual order, retained once."""
        assert dimension >= 0
        simplex = Sets().Simplex(dimension)
        usual_order = (simplex * simplex).subset_from(lambda pair: pair(0) <= pair(1))
        # The usual order on {0, ..., n} is a linear order: Mathlib ``Nat.instLinearOrder``
        # restricted along ``Subtype.instLinearOrder`` (inspected 2026-08-27).
        return self.TotallyOrdered()(self._construct(usual_order))

    @cached_method
    def Terminal(self) -> Poset:
        """The one-point order on ``Sets().Terminal()``, the terminal object of ``Posets()``."""
        point = Sets().Terminal()
        return self.TotallyOrdered()(self._construct((point * point).subset_from(lambda pair: True)))

    @cached_method(key=lambda self, base_set: (id(base_set), base_set))
    def subset_poset(self, base_set: SetObject) -> Poset:
        """The power object ``2 ** X`` ordered by inclusion of the subsets its points name, retained per ``X``.

        The order relation is the chosen subset of ``(2 ** X) * (2 ** X)`` of the pairs
        ``(chi_A, chi_B)`` with ``A <= B``; containment is a partial order (nLab "power
        set": "the power set canonically carries a partial order by containment";
        inspected 2026-08-27), so the poset is constructed directly (POL-MATH-037).
        ``2 ** X`` retains ``X`` as its base set (``sets/power_objects.py``).
        """
        power = Sets().Simplex(1) ** base_set

        def included(pair: Datum) -> Decision:
            return ask(power.from_characteristic_morphism(pair(0).map()) <= power.from_characteristic_morphism(pair(1).map()))

        return self._construct((power * power).subset_from(included))

    @cached_method
    def Finite(self) -> Category[[Rule], []]:
        """``FinitePosets()``: the property subcategory by finiteness of the underlying set (``posets/finite.py``), constructed once.

        The category is retained as the chosen pullback ``U.inverse_image(Sets().Finite())``
        (``specs/ordered-sets.md``), so both routes return this one value.
        """
        from sage_categories.cat.properties import retain_inverse_image
        from sage_categories.posets.finite import FinitePosetsCategory

        finite = FinitePosetsCategory(self, "Finite", ())
        retain_inverse_image(
            self.underlying_set_functor(),
            Sets().Finite(),
            finite,
            finite.structure_functors()[0],
            finite.underlying_finite_set_functor(),
        )
        return finite

    def TotallyOrdered(self) -> Category[[Rule], []]:
        return self._totally_ordered

    # -- elements ---------------------------------------------------------------------------

    def element_from_defining_morphism(self, defining_morphism: MonotoneMap) -> PosetElement:
        """The generalized element defined by ``T -> P``, retained by that exact map (POL-CAT-066).

        A point adds no local state: the underlying set point of ``t: * -> P``
        is ``U(t)``, which the selected functor supplies on demand.  ``Poset.element``
        owns the point of one set element; it reaches this constructor.
        """
        assert defining_morphism in self.morphism_category(1)
        if defining_morphism not in self._elements:
            self._elements[defining_morphism] = defining_morphism.codomain().category().ElementType(defining_morphism, None)
        return self._elements[defining_morphism]

    # -- morphisms ------------------------------------------------------------------------------

    def construct_morphism(self, domain: Poset, codomain: Poset, rule: Rule | SetMap) -> MonotoneMap:
        """``Mor(Posets())(P, Q)(rule)``: the monotone map whose underlying set map has this rule."""
        assert domain in self and codomain in self
        underlying = self.underlying_set_functor()
        u_dom = underlying.on_object(domain)
        u_cod = underlying.on_object(codomain)
        if role_of(rule) is Role.MORPHISM:
            assert ask(rule.domain() == u_dom) is True and ask(rule.codomain() == u_cod) is True, (
                f"{rule!r} endpoints do not match {domain!r} -> {codomain!r}"
            )
            set_map = rule
        else:
            set_map = Sets().morphism_category(1)(u_dom, u_cod)(rule)
        assert ask(self.is_order_preserving(domain, codomain, set_map)) is not False, f"{set_map!r} is not monotone"
        return self._construct_morphism(domain, codomain, set_map)

    def _construct_morphism(self, domain: Poset, codomain: Poset, set_map: SetMap) -> MonotoneMap:
        """Construct a monotone map whose supplied set map is established by its caller."""
        return self.MorphismType(self.morphism_category(1), domain, codomain, PosetMorphismData(set_map))

    def construct_identity(self, poset: Poset) -> MonotoneMap:
        # The identity is monotone: Mathlib ``OrderHom.id``.
        return self._construct_morphism(poset, poset, self.underlying_set_functor().on_object(poset).identity())

    def composite(self, second: MonotoneMap, first: MonotoneMap) -> MonotoneMap:
        # Monotone maps compose: Mathlib ``OrderHom.comp``.
        morphisms = self.morphism_category(1)
        assert first in morphisms and second in morphisms
        assert first.codomain() is second.domain(), f"{second!r} after {first!r} is not composable"
        underlying = self.underlying_set_functor()
        set_map = underlying.on_morphism(second) * underlying.on_morphism(first)
        return self._construct_morphism(first.domain(), second.codomain(), set_map)

    def inverse_morphism(self, monotone: MonotoneMap) -> MonotoneMap:
        """The inverse of an order isomorphism: the inverse set map is monotone (Mathlib ``OrderIso.symm``)."""
        if monotone not in self._inverses:
            set_map = self.underlying_set_functor().on_morphism(monotone).inverse()
            inverse = self._construct_morphism(monotone.codomain(), monotone.domain(), set_map)
            self.retain_inverses(monotone, inverse)
        return self._inverses[monotone]

    def _induced_order(self, monomorphism: SetMap, target: Poset) -> MonotoneMap:
        """The cartesian lift of ``m: Y -> U(P)`` at ``P`` that ``U`` retains: the sub-poset ``(Y, R restricted to Y)`` with ``m`` monotone.

        The induced order is the ``U``-initial lift of the monomorphism (AHS Definition
        10.41, Example 10.42(6); Mathlib ``PartialOrder.lift``); ``U`` lifts exactly
        the monomorphisms of ``Sets()`` (POL-LEAF-024, POL-SCOPE-011).
        """
        assert target in self and monomorphism in Sets().morphism_category(1).Monomorphisms(), f"{monomorphism!r} is not a monomorphism into the underlying set of {target!r}"
        subset = monomorphism.domain()

        def induced(pair: Datum) -> Decision:
            left, right = monomorphism(subset.point(pair(0))), monomorphism(subset.point(pair(1)))
            return ask(target.relation().membership_proposition(target._pair(left, right)))

        sub_poset = self._construct((subset * subset).subset_from(induced))
        return self._construct_morphism(sub_poset, target, monomorphism)

    # -- equality (POL-API-015, POL-SET-026) ----------------------------------------------------------------

    def _equal(self, first: CategoryOfCategories.ElementType, candidate: Any) -> Decision:
        """Classical elements of one poset are equal when their points are; monotone maps when their set maps are."""
        if _is_point(first) and _is_point(candidate) and first.parent() is candidate.parent():
            underlying = self.underlying_set_functor()
            return ask(underlying.on_element(first) == underlying.on_element(candidate))
        morphisms = self.morphism_category(1)
        if first in morphisms and candidate in morphisms:
            underlying = self.underlying_set_functor()
            return ask(underlying.on_morphism(first) == underlying.on_morphism(candidate))
        return Unknown

    @cached_method(key=lambda self, base_set: (id(base_set), base_set))
    def discrete_order(self, base_set: SetObject) -> Poset:
        """The discrete order on ``base_set``: ``x <= y`` iff ``x == y``."""
        assert base_set in Sets(), f"{base_set!r} is not a set"
        square = base_set * base_set
        relation = square.subset_from(lambda pair: pair(0) == pair(1))
        return self._construct(relation)

    def binary_product(self, first: Poset, second: Poset) -> Poset:
        """Binary product poset with the coordinatewise partial order (specs/ordered-sets.md)."""
        assert first in self and second in self
        U = self.underlying_set_functor()
        set_first, set_second = U.on_object(first), U.on_object(second)
        prod_set = set_first * set_second

        def componentwise_le(pair_of_pairs: Datum) -> Decision:
            left_pair, right_pair = pair_of_pairs(0), pair_of_pairs(1)
            x0, y0 = left_pair(0), left_pair(1)
            x1, y1 = right_pair(0), right_pair(1)
            x_le = ask(first.element(set_first.point(x0)) <= first.element(set_first.point(x1)))
            y_le = ask(second.element(set_second.point(y0)) <= second.element(set_second.point(y1)))
            return ask(conjunction((x_le, y_le)))

        prod_square = prod_set * prod_set
        relation = prod_square.subset_from(componentwise_le)
        return self._construct(relation)

    @cached_method
    def thin_functor(self) -> Functor:
        """``Thin: Posets() -> Cat()``: named functor constructing thin categories (specs/ordered-sets.md)."""
        from sage_categories.cat.category import Cat

        def on_poset(poset: Poset) -> ThinCategory:
            return poset.thin_category()

        def on_monotone_map(monotone: MonotoneMap) -> Functor:
            source_thin = monotone.domain().thin_category()
            target_thin = monotone.codomain().thin_category()
            set_map = self.underlying_set_functor().on_morphism(monotone)
            return Fun(source_thin, target_thin)(
                lambda obj: target_thin(set_map(obj.point())),
                lambda mor: target_thin.construct_morphism(
                    target_thin(set_map(mor.domain().point())),
                    target_thin(set_map(mor.codomain().point())),
                ),
            )

        return Fun(self, Cat())(on_poset, on_monotone_map)

    def __repr__(self) -> str:
        return "Posets"


_POSETS = PosetsCategory()
Poset = _POSETS.ObjectType
PosetElement = _POSETS.ElementType
MonotoneMap = _POSETS.MorphismType


def _covers_on_finite(
    poset: CategoryOfCategories.ElementType,
    lower: CategoryOfCategories.ElementType,
    upper: CategoryOfCategories.ElementType,
    assumptions: Proposition,
) -> Decision:
    from sage_categories.posets import _finite_poset_sage as engine

    if poset in _POSETS.Finite():
        return bool(engine.sage_poset(poset).covers(engine.datum(poset, lower), engine.datum(poset, upper)))
    return Unknown


# Deferred handler registrations (see __init__ comment).
partial_order.register_handler(_partial_order_on_enumerated)
order_preserving.register_handler(_order_preserving_on_enumerated)
covers.register_handler(_covers_on_finite)
_POSETS._totally_ordered.predicate().register_handler(_total_on_enumerated)


def Posets() -> PosetsCategory:
    """The category of partially ordered sets."""
    return _POSETS


def FinitePosets() -> Category[[Rule], []]:
    """``Posets().Finite()``: the finite posets."""
    return _POSETS.Finite()


def TotallyOrderedSets() -> Category[[Rule], []]:
    """``Posets().TotallyOrdered()``: the totally ordered sets."""
    return _POSETS.TotallyOrdered()


def FiniteTotallyOrderedSets() -> Category[[Rule], []]:
    """``Posets().Finite().TotallyOrdered()``: the finite totally ordered sets."""
    return _POSETS.Finite().TotallyOrdered()


class SimplexOrdersFamily:
    """The canonical simplex orders [n] on {0, ..., n}."""

    def __getitem__(self, dimension: int | Integer) -> Poset:
        return Posets().Simplex(dimension)


def SimplexOrders() -> SimplexOrdersFamily:
    """``SimplexOrders()[n]``: the canonical total order on {0, ..., n}."""
    return SimplexOrdersFamily()


def thin_functor() -> Functor:
    """``Thin: Posets() -> Cat()``: named functor constructing thin categories."""
    return _POSETS.thin_functor()


Thin: Functor = _POSETS.thin_functor()

