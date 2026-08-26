"""``Posets()``: partially ordered sets and monotone maps (``specs/ordered-sets.md``).

A poset is a pair ``(X, R)`` with ``R`` a chosen subset of ``X * X`` (``sets/subobjects.py``).
``Posets()(R)`` recovers ``X`` as the factor of the chosen product that ``R`` is a
subset of, asserts that both factors are one set (POL-LEAF-002), and trusts that ``R``
is a partial order (POL-CAT-069, POL-MATH-037); ``Posets().is_partial_order(R)`` is the
owned predicate whose exact handler decides reflexivity, antisymmetry, and
transitivity on a finite enumerated carrier (POL-MATH-042).

The one selected structural functor is the underlying-set functor
``U: Posets() -> Sets()``.  It is faithful because ``Pos`` is a construct (Mathlib
``PartOrd.instConcreteCategoryOrderHomCarrier``; inspected 2026-08-27).  It returns the
retained ``X`` of a poset and the retained set map of a monotone map, and it supplies
the complete set surface: every inherited method returns the declaring method's value
in ``Sets()`` (POL-CAT-062).  A poset is never placed in ``Sets()``; it reaches every
set operation through ``U`` alone.  The classical stage is the one-point order
``Posets().Terminal()``; ``U`` carries the identity stage comparison because the
underlying set of the one-point order is ``Sets().Terminal()`` by construction.  For
classical elements ``x, y`` of ``P``, ``x <= y`` is the membership proposition of the
pair point ``(x, y): 1 -> X * X`` in ``R``.

A monotone map ``Mor(Posets())(P, Q)(rule)`` retains its underlying set map; identities
and composites are monotone (Mathlib ``OrderHom.id``, ``OrderHom.comp``; inspected
2026-08-27), and the inverse of an order isomorphism is monotone (Mathlib
``OrderIso.symm``, ``OrderIso.monotone``; inspected 2026-08-27).  ``U`` retains the
cartesian lift of every monomorphism ``m: Y -> U(P)`` of ``Sets()`` at ``P``: the induced
order on ``Y`` is the ``U``-initial lift of ``m`` (Adamek, Herrlich, Strecker, *Abstract
and Concrete Categories*, Definition 10.41 and Example 10.42(6), inspected 2026-08-26;
Mathlib ``PartialOrder.lift``, inspected 2026-08-27).  ``P.sub_poset(...)`` is the leaf
override of POL-LEAF-029/030: it calls the inherited subset construction and lifts.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category
from sage_categories.cat.constructions import cone
from sage_categories.cat.diagrams import sequence_position
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.shapes import ThinCategory
from sage_categories.kernel.decisions import Decision, Unknown, decision_and, decision_not, decision_or
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, Proposition, ask
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of
from sage_categories.sets.category import Sets
from sage_categories.sets.elements import Datum, SetPoint
from sage_categories.sets.maps import Rule, SetMap
from sage_categories.sets.objects import MembershipRule, SetObject

__all__ = ["FinitePosets", "FiniteTotallyOrderedSets", "MonotoneMap", "Poset", "PosetElement", "Posets", "PosetsCategory", "TotallyOrderedSets"]

# ``partial_order(R)``: the relation ``R`` on ``X`` is reflexive, antisymmetric, and transitive.
partial_order = Predicate("partial_order", 1, True)
# ``order_preserving(P, Q, f)``: the set map ``f: U(P) -> U(Q)`` is monotone.
order_preserving = Predicate("order_preserving", 3, False)

type Relation = dict[tuple[int, int], Decision]


class Poset(ObjectOfCategory):
    """A partially ordered set ``(X, R)``; the set surface arrives through ``U``."""

    def __init__(self, category: Category, underlying_set: SetObject, relation: SetObject) -> None:
        ObjectOfCategory.__init__(self, category)
        self._underlying_set = underlying_set
        self._relation = relation
        self._square = Sets().Products()((underlying_set, underlying_set))
        self._elements: MonoDict = MonoDict()

    def relation(self) -> SetObject:
        """The defining order relation ``R``, a chosen subset of ``X * X``."""
        return self._relation

    def element(self, point: SetPoint) -> PosetElement:
        """The classical element over a point ``x: 1 -> U(P)``: the monotone map ``1 -> P`` under ``x``."""
        assert point in self._underlying_set, f"{point!r} is not a point of {self._underlying_set!r}"
        if point not in self._elements:
            posets = Posets()
            defining_morphism = posets.MorphismType(posets.morphism_category(1), posets.Terminal(), self, point.defining_morphism())
            self._elements[point] = self.category().ElementType(defining_morphism)
        return self._elements[point]

    def sub_poset(self, predicate: MembershipRule) -> Poset:
        """The sub-poset ``{x in P : predicate(x)}`` with the induced order (POL-LEAF-029/030).

        The inherited subset construction supplies the subset of ``U(P)``; the
        cartesian lift retained by ``U`` supplies the induced order.
        """
        subset = self.subset_from(predicate)
        return Posets().underlying_set_functor().cartesian_lift(subset.inclusion(), self).domain()

    def is_total(self) -> AppliedPredicate:
        """Totality: any two elements are comparable."""
        return Posets().TotallyOrdered().predicate()(self)

    def thin_category(self) -> ThinCategory:
        """The thin category of ``P``: objects the points of ``U(P)``, one comparison per related pair; retained once."""
        retained = Posets()._thin
        if self not in retained:
            order = Predicate("poset_order", 2, True)
            order.register_handler(lambda left, right: ask(self.element(left) <= self.element(right)))
            retained[self] = ThinCategory(self._underlying_set, order)
        return retained[self]

    def _pair(self, left: SetPoint, right: SetPoint) -> SetPoint:
        return _pair_point(self._square, left, right)

    def __repr__(self) -> str:
        return f"Poset({self._underlying_set!r})"


class PosetElement(ElementOfObject):
    """A generalized element ``t: T -> P``; the order compares classical elements."""

    def __init__(self, defining_morphism: MonotoneMap) -> None:
        ElementOfObject.__init__(self, defining_morphism)

    def __le__(self, other: PosetElement) -> AppliedPredicate:
        """``x <= y``: the pair point ``(U(x), U(y))`` is a member of ``R``."""
        poset = self.parent()
        assert _is_classical(self) and _is_classical(other), f"{self!r} <= {other!r} compares classical elements"
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
        return f"point of {self.parent()!r} at stage {self.stage()!r}"


class MonotoneMap(MorphismOfCategory):
    """A monotone map ``P -> Q``, retaining its underlying set map."""

    def __init__(self, category: Category, domain: Poset, codomain: Poset, set_map: SetMap) -> None:
        MorphismOfCategory.__init__(self, category, domain, codomain)
        self._set_map = set_map

    def __repr__(self) -> str:
        return f"MonotoneMap({self.domain()!r} -> {self.codomain()!r})"


# -- exact handlers on finite enumerated carriers (POL-MATH-042) --------------------------


def _is_classical(candidate: Any) -> bool:
    posets = Posets()
    return role_of(candidate) is Role.ELEMENT and candidate.parent() in posets and candidate.stage() is posets.Terminal()


def _enumerated_points(carrier: SetObject) -> tuple[SetPoint, ...]:
    assert Sets().Finite().has_chosen_enumeration(carrier)
    return tuple(carrier)


def _decided(decide: Callable[[SetPoint, SetPoint], Decision], points: tuple[SetPoint, ...]) -> Relation:
    """The relation on ``points`` decided pairwise, memoized by position."""
    return {(i, j): decide(left, right) for i, left in enumerate(points) for j, right in enumerate(points)}


def _reflexive(relation: Relation, size: int) -> Decision:
    return decision_and(*(relation[i, i] for i in range(size)))


def _antisymmetric(relation: Relation, size: int) -> Decision:
    return decision_and(*(decision_not(decision_and(relation[i, j], relation[j, i])) for i in range(size) for j in range(i + 1, size)))


def _transitive(relation: Relation, size: int) -> Decision:
    return decision_and(
        *(
            decision_or(decision_not(decision_and(relation[i, j], relation[j, k])), relation[i, k])
            for i in range(size)
            for j in range(size)
            for k in range(size)
        )
    )


def _total(relation: Relation, size: int) -> Decision:
    return decision_and(*(decision_or(relation[i, j], relation[j, i]) for i in range(size) for j in range(i + 1, size)))


def _partial_order_on_enumerated(relation: SetObject) -> Decision:
    sets = Sets()
    if relation not in sets.ChosenSubsets():
        return Unknown
    square = relation.underlying_set()
    carrier = square.product_projection(0).codomain()
    if not sets.Finite().has_chosen_enumeration(carrier):
        return Unknown
    points = _enumerated_points(carrier)
    pairs = _decided(lambda left, right: ask(relation.membership_proposition(_pair_point(square, left, right))), points)
    return decision_and(_reflexive(pairs, len(points)), _antisymmetric(pairs, len(points)), _transitive(pairs, len(points)))


def _pair_point(square: ObjectOfCategory, left: SetPoint, right: SetPoint) -> SetPoint:
    """The point ``(left, right): 1 -> X * X``: the mediator of the cone with these legs."""
    legs = (left.defining_morphism(), right.defining_morphism())
    pairing = cone(square.diagram(), Sets().Terminal(), lambda vertex: legs[sequence_position(vertex)])
    return Sets().element_from_defining_morphism(square.universal_morphism(pairing))


def _order_relation(poset: Poset, points: tuple[SetPoint, ...]) -> Relation:
    return _decided(lambda left, right: ask(poset.element(left) <= poset.element(right)), points)


def _total_on_enumerated(poset: CategoryPoint) -> Decision:
    posets = Posets()
    if poset not in posets:
        return Unknown
    carrier = posets.underlying_set_functor().on_object(poset)
    if not Sets().Finite().has_chosen_enumeration(carrier):
        return Unknown
    points = _enumerated_points(carrier)
    return _total(_order_relation(poset, points), len(points))


def _order_preserving_on_enumerated(source: Poset, target: Poset, set_map: SetMap) -> Decision:
    carrier = Posets().underlying_set_functor().on_object(source)
    if not Sets().Finite().has_chosen_enumeration(carrier):
        return Unknown
    points = _enumerated_points(carrier)
    images = tuple(set_map(point) for point in points)
    domain_order, codomain_order = _order_relation(source, points), _order_relation(target, images)
    return decision_and(
        *(decision_or(decision_not(domain_order[i, j]), codomain_order[i, j]) for i in range(len(points)) for j in range(len(points)))
    )


class PosetsCategory(Category[[Rule], []]):
    """The category of partially ordered sets and monotone maps."""

    ObjectType = Poset
    ElementType = PosetElement
    MorphismType = MonotoneMap

    def __init__(self) -> None:
        self._functors: dict[str, Functor] = {}
        self._canonical: dict[tuple[str, int], Poset] = {}
        self._thin: MonoDict = MonoDict()
        super().__init__()
        self.underlying_set_functor().retain_cartesian_lifts(self._induced_order)
        self._equality.register_handler(self._equal)
        partial_order.register_handler(_partial_order_on_enumerated)
        order_preserving.register_handler(_order_preserving_on_enumerated)
        totally_ordered = PropertySubcategory(self, "TotallyOrdered", {}, ())
        totally_ordered.predicate().register_handler(_total_on_enumerated)
        self._properties["TotallyOrdered"] = totally_ordered

    # -- the selected structural functor -------------------------------------------

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.underlying_set_functor(),)

    def underlying_set_functor(self) -> Functor:
        """``U: Posets() -> Sets()``, retained once: the retained carrier and the retained set map."""
        if "underlying_set" not in self._functors:
            self._functors["underlying_set"] = Fun(self, Sets()).Faithful()(lambda poset: poset._underlying_set, lambda monotone: monotone._set_map)
        return self._functors["underlying_set"]

    def classical_stages(self) -> tuple[Poset, ...]:
        return (self.Terminal(),)

    # -- construction (POL-CAT-069, POL-LEAF-002) ----------------------------------------

    def __call__(self, relation: SetObject) -> Poset:
        """``Posets()(R)``: the poset on the factor ``X`` of ``X * X`` that ``R`` is a subset of."""
        assert relation in Sets().ChosenSubsets(), f"{relation!r} is not a chosen subset"
        underlying_set = self._carrier(relation)
        assert ask(self.is_partial_order(relation)) is not False, f"{relation!r} is not a partial order"
        return self._construct(underlying_set, relation)

    def _carrier(self, relation: SetObject) -> SetObject:
        square = relation.underlying_set()
        assert square in Sets().Products(), f"{relation!r} is not a subset of a chosen product"
        first, second = square.product_projection(0).codomain(), square.product_projection(1).codomain()
        assert first is second, f"{relation!r} is a subset of a product of two distinct sets"
        return first

    def _construct(self, underlying_set: SetObject, relation: SetObject) -> Poset:
        # A poset on a finite set is a finite poset by definition (POL-CAT-081).
        poset = self.ObjectType(self, underlying_set, relation)
        if underlying_set in Sets().Finite():
            self.Finite()(poset)
        return poset

    def is_partial_order(self, relation: SetObject) -> AppliedPredicate:
        """The proposition that a chosen subset of ``X * X`` is reflexive, antisymmetric, and transitive."""
        return partial_order(relation)

    def is_order_preserving(self, source: Poset, target: Poset, set_map: SetMap) -> AppliedPredicate:
        """The proposition that a set map ``U(P) -> U(Q)`` is monotone."""
        return order_preserving(source, target, set_map)

    def Simplex(self, dimension: int) -> Poset:
        """``[n]``: the poset on ``Sets().Simplex(n)`` with the usual order, retained once."""
        assert dimension >= 0
        if ("simplex", dimension) not in self._canonical:
            simplex = Sets().Simplex(dimension)
            usual_order = (simplex * simplex).subset_from(lambda pair: pair(0) <= pair(1))
            # The usual order on {0, ..., n} is a linear order: Mathlib ``Nat.instLinearOrder``
            # restricted along ``Subtype.instLinearOrder`` (inspected 2026-08-27).
            self._canonical["simplex", dimension] = self.TotallyOrdered()(self._construct(simplex, usual_order))
        return self._canonical["simplex", dimension]

    def Terminal(self) -> Poset:
        """The one-point order on ``Sets().Terminal()``, the classical stage of ``Posets()``."""
        if ("terminal", 0) not in self._canonical:
            point = Sets().Terminal()
            self._canonical["terminal", 0] = self.TotallyOrdered()(self._construct(point, (point * point).subset_from(lambda pair: True)))
        return self._canonical["terminal", 0]

    def Finite(self) -> Category[[Rule], []]:
        """``FinitePosets()``: the property subcategory by finiteness of the underlying set (``posets/finite.py``)."""
        if "Finite" not in self._properties:
            from sage_categories.posets.finite import FinitePosetRole, FinitePosetsCategory

            self._properties["Finite"] = FinitePosetsCategory(self, "Finite", {Role.OBJECT: FinitePosetRole}, ())
        return self._properties["Finite"]

    def TotallyOrdered(self) -> Category[[Rule], []]:
        return self._properties["TotallyOrdered"]

    # -- elements ---------------------------------------------------------------------------

    def element_from_defining_morphism(self, defining_morphism: MonotoneMap) -> PosetElement:
        """The classical element over the point ``U(t)`` when ``t: 1 -> P``; the generalized element ``t`` otherwise."""
        assert defining_morphism in self.morphism_category(1)
        if defining_morphism.domain() is self.Terminal():
            return defining_morphism.codomain().element(Sets().element_from_defining_morphism(defining_morphism._set_map))
        return defining_morphism.codomain().category().ElementType(defining_morphism)

    # -- morphisms ------------------------------------------------------------------------------

    def construct_morphism(self, domain: Poset, codomain: Poset, rule: Rule) -> MonotoneMap:
        """``Mor(Posets())(P, Q)(rule)``: the monotone map whose underlying set map has this rule."""
        assert domain in self and codomain in self
        underlying = self.underlying_set_functor()
        set_map = Sets().morphism_category(1)(underlying.on_object(domain), underlying.on_object(codomain))(rule)
        assert ask(self.is_order_preserving(domain, codomain, set_map)) is not False, f"{set_map!r} is not monotone"
        return self.MorphismType(self.morphism_category(1), domain, codomain, set_map)

    def construct_identity(self, poset: Poset) -> MonotoneMap:
        # The identity is monotone: Mathlib ``OrderHom.id``.
        return self.MorphismType(self.morphism_category(1), poset, poset, self.underlying_set_functor().on_object(poset).identity())

    def composite(self, second: MonotoneMap, first: MonotoneMap) -> MonotoneMap:
        # Monotone maps compose: Mathlib ``OrderHom.comp``.
        morphisms = self.morphism_category(1)
        assert first in morphisms and second in morphisms
        assert first.codomain() is second.domain(), f"{second!r} after {first!r} is not composable"
        return self.MorphismType(morphisms, first.domain(), second.codomain(), second._set_map * first._set_map)

    def inverse_morphism(self, monotone: MonotoneMap) -> MonotoneMap:
        """The inverse of an order isomorphism: the inverse set map is monotone (Mathlib ``OrderIso.symm``)."""
        if monotone not in self._inverses:
            inverse = self.MorphismType(self.morphism_category(1), monotone.codomain(), monotone.domain(), monotone._set_map.inverse())
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

        sub_poset = self._construct(subset, (subset * subset).subset_from(induced))
        return self.MorphismType(self.morphism_category(1), sub_poset, target, monomorphism)

    # -- equality (POL-API-015, POL-SET-026) ----------------------------------------------------------------

    def _equal(self, first: CategoryPoint, candidate: Any) -> Decision:
        """Classical elements of one poset are equal when their points are; monotone maps when their set maps are."""
        if _is_classical(first) and _is_classical(candidate) and first.parent() is candidate.parent():
            underlying = self.underlying_set_functor()
            return ask(underlying.on_element(first) == underlying.on_element(candidate))
        morphisms = self.morphism_category(1)
        if first in morphisms and candidate in morphisms:
            return ask(first._set_map == candidate._set_map)
        return Unknown

    def __repr__(self) -> str:
        return "Posets"


_POSETS = PosetsCategory()


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
