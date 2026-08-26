"""Diagram shapes supplied by the kernel: ``Discrete(S)`` and ``Thin(P, leq)`` (POL-SET-013, POL-SET-014).

``Discrete`` is a functor ``Sets() -> Cat()`` retained once.  ``Discrete(S)`` is the
discrete category on the set ``S``: its objects are the classical points of ``S``
and its morphisms are identities only (Mathlib ``CategoryTheory.Discrete`` and
``CategoryTheory.discreteCategory``; inspected 2026-08-26).  No enumeration of
``S`` occurs: an object ``Discrete(S)(x)`` is constructed from a point ``x`` whose
membership in ``S`` is asserted, and two objects are equal exactly when their
points are.  A set map ``f: S -> T`` is sent to the functor ``Discrete(S) ->
Discrete(T)`` acting on points by ``f``.

``Thin(P, leq)`` is the thin category of a preorder given as a set ``P`` with an
order predicate ``leq``: objects are the points of ``P`` and there is at most one
morphism ``x -> y``, which exists when ``ask(leq(x, y)) is True`` (Mathlib
``Preorder.smallCategory`` and ``Preorder.subsingleton_hom``; inspected
2026-08-26).  The writer asserts reflexivity and transitivity (POL-MATH-037):
identities and composites are the unique comparisons.  The sequential shape
``omega`` is ``Thin(NN, leq)`` for the natural order of ``NN`` (``specs/sets.md``,
"General limits and colimits"); ``NN`` is an owned set, and the order predicate
that makes it a preorder is supplied by the caller of ``Thin``.

Finite presented shapes are ``FinitePresentedCategory`` (``cat/canonical.py``),
constructed uniformly by ``Cat()(labels, generators, relations)``.
"""

from __future__ import annotations

from typing import Any

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass, decision_and
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.category import Sets
from sage_categories.sets.elements import SetPoint
from sage_categories.sets.maps import SetMap
from sage_categories.sets.objects import SetObject

__all__ = ["Discrete", "DiscreteCategory", "Thin", "ThinCategory", "index_set_of", "is_discrete", "omega"]


# -- Discrete(S) ---------------------------------------------------------------------


class DiscreteObject(ObjectOfCategory):
    """An object of ``Discrete(S)``: a classical point of ``S``."""

    def __init__(self, category: Category, point: SetPoint) -> None:
        super().__init__(category)
        self._point = point

    def point(self) -> SetPoint:
        """The point of the index set that this object is."""
        return self._point

    def __repr__(self) -> str:
        return f"{self._point!r} in {self.category()!r}"


class DiscreteIdentity(MorphismOfCategory):
    """The only morphisms of a discrete category: identities."""

    def __repr__(self) -> str:
        return f"identity of {self.domain()!r}"


class DiscreteCategory(Category[[], []]):
    """The discrete category on a set."""

    ObjectType = DiscreteObject
    MorphismType = DiscreteIdentity

    class ElementType(ElementOfObject):
        """A generalized element of a point; no local operation."""

    def __init__(self, index_set: SetObject) -> None:
        self._index_set = index_set
        self._objects: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(self._equal)

    def index_set(self) -> SetObject:
        return self._index_set

    # The objects are the points of ``S`` and the morphisms their identities (specs/functor.md, "Diagram shapes and universal constructions").

    def object_set(self) -> SetObject:
        return self._index_set

    def object_at(self, point: SetPoint) -> DiscreteObject:
        return self(point)

    def object_point(self, member_object: DiscreteObject) -> SetPoint:
        return member_object.point()

    def morphism_set(self) -> SetObject | UnknownClass:
        return self._index_set

    def morphism_at(self, point: SetPoint) -> DiscreteIdentity:
        return self(point).identity()

    def generating_morphisms(self) -> tuple[DiscreteIdentity, ...]:
        """No morphism beyond the identities: the empty generating family."""
        return ()

    def __call__(self, point: SetPoint) -> DiscreteObject:
        """The object of ``Discrete(S)`` at a point of ``S``, one object per retained point."""
        assert point in self._index_set, f"{point!r} is not a point of {self._index_set!r}"
        if point not in self._objects:
            self._objects[point] = self.ObjectType(self, point)
        return self._objects[point]

    def construct_morphism(self, domain: DiscreteObject, codomain: DiscreteObject) -> DiscreteIdentity:
        """``Mor(Discrete(S))(x, y)()``: the identity, which exists exactly when ``x == y``."""
        assert ask(domain == codomain) is True, f"{self!r} has no morphism {domain!r} -> {codomain!r}"
        return self.MorphismType(self.morphism_category(1), domain, codomain)

    def construct_identity(self, member_object: DiscreteObject) -> DiscreteIdentity:
        return self.MorphismType(self.morphism_category(1), member_object, member_object)

    def composite(self, second: DiscreteIdentity, first: DiscreteIdentity) -> DiscreteIdentity:
        assert ask(first.codomain() == second.domain()) is True
        return self.MorphismType(self.morphism_category(1), first.domain(), second.codomain())

    def _equal(self, first: CategoryPoint, candidate: Any) -> Decision:
        """Objects are equal when their points are; morphisms when their domains are."""
        if first in self and candidate in self:
            return ask(first.point() == candidate.point())
        morphisms = self.morphism_category(1)
        if first in morphisms and candidate in morphisms:
            return ask(first.domain() == candidate.domain())
        return Unknown

    def __repr__(self) -> str:
        return f"Discrete({self._index_set!r})"


# The retained images of the ``Discrete`` functor: ``S |-> Discrete(S)`` and, for
# ``index_set_of``, ``Discrete(S) |-> S``; both keyed by identity.
_discrete_categories: MonoDict = MonoDict()
_index_sets: MonoDict = MonoDict()
_discrete_functors: MonoDict = MonoDict()


def _discrete_on_object(index_set: SetObject) -> DiscreteCategory:
    if index_set not in _discrete_categories:
        shape = DiscreteCategory(index_set)
        _discrete_categories[index_set] = shape
        _index_sets[shape] = index_set
    return _discrete_categories[index_set]


def _discrete_on_morphism(set_map: SetMap) -> Functor:
    if set_map not in _discrete_functors:
        source, target = _discrete_on_object(set_map.domain()), _discrete_on_object(set_map.codomain())
        _discrete_functors[set_map] = Fun(source, target)(
            lambda vertex: target(set_map(vertex.point())),
            lambda identity: target(set_map(identity.domain().point())).identity(),
        )
    return _discrete_functors[set_map]


# The functor ``Discrete: Sets() -> Cat()``, retained once; ``Discrete(S)`` is its
# object action and ``Discrete(f)`` its morphism action (Mathlib
# ``CategoryTheory.Discrete.functor`` for the action on maps; inspected 2026-08-26).
Discrete: Functor = Fun(Sets(), Cat())(_discrete_on_object, _discrete_on_morphism)


def is_discrete(shape: Category) -> bool:
    """Whether ``shape`` is a retained image ``Discrete(S)``."""
    return shape in _index_sets


def index_set_of(shape: Category) -> SetObject:
    """The set ``S`` with ``shape is Discrete(S)``."""
    assert is_discrete(shape), f"{shape!r} is not Discrete(S) for a set S"
    return _index_sets[shape]


# -- Thin(P, leq) --------------------------------------------------------------------


class ThinObject(ObjectOfCategory):
    """An object of ``Thin(P, leq)``: a point of ``P``."""

    def __init__(self, category: Category, point: SetPoint) -> None:
        super().__init__(category)
        self._point = point

    def point(self) -> SetPoint:
        return self._point

    def __repr__(self) -> str:
        return f"{self._point!r} in {self.category()!r}"


class Comparison(MorphismOfCategory):
    """The unique morphism ``x -> y`` of a thin category, present when ``x <= y``."""

    def __repr__(self) -> str:
        return f"{self.domain()!r} <= {self.codomain()!r}"


# ``comparable(f, T)``: the endpoints of the comparison ``f`` of ``T`` satisfy ``T``'s order.
comparable = Predicate("comparable", 2, False)


def _comparable_by_order(candidate: CategoryPoint, thin: Category) -> Decision:
    if not is_placed(candidate, thin.morphism_category(1)):
        return Unknown
    return ask(thin.order()(candidate.domain().point(), candidate.codomain().point()))


comparable.register_handler(_comparable_by_order)


class ThinMorphisms(MorphismCategory[[], []]):
    """``Mor(Thin(P, leq))``: a comparison is a member when its order proposition holds."""

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return member(candidate, self) & comparable(candidate, self._base)


class ThinCategory(Category[[], []]):
    """The thin category of a preorder ``(P, leq)``."""

    ObjectType = ThinObject
    MorphismType = Comparison

    class ElementType(ElementOfObject):
        """A generalized element of a point; no local operation."""

    def __init__(self, carrier: SetObject, order: Predicate) -> None:
        assert order.arity() == 2
        self._carrier = carrier
        self._order = order
        self._objects: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(self._equal)

    def carrier(self) -> SetObject:
        return self._carrier

    def order(self) -> Predicate:
        return self._order

    def morphism_category_type(self) -> type[ThinMorphisms]:
        return ThinMorphisms

    # The objects are the points of ``P``; no finite family of comparisons is chosen.

    def object_set(self) -> SetObject:
        return self._carrier

    def object_at(self, point: SetPoint) -> ThinObject:
        return self(point)

    def object_point(self, member_object: ThinObject) -> SetPoint:
        return member_object.point()

    def __call__(self, point: SetPoint) -> ThinObject:
        """The object at a point of ``P``, one object per retained point."""
        assert point in self._carrier, f"{point!r} is not a point of {self._carrier!r}"
        if point not in self._objects:
            self._objects[point] = self.ObjectType(self, point)
        return self._objects[point]

    def construct_morphism(self, domain: ThinObject, codomain: ThinObject) -> Comparison:
        """``Mor(Thin)(x, y)()``: the comparison ``x <= y``; rejected only when the order decides against it."""
        assert ask(self._order(domain.point(), codomain.point())) is not False, f"{domain!r} <= {codomain!r} is false"
        return self.MorphismType(self.morphism_category(1), domain, codomain)

    def construct_identity(self, member_object: ThinObject) -> Comparison:
        return self.MorphismType(self.morphism_category(1), member_object, member_object)

    def composite(self, second: Comparison, first: Comparison) -> Comparison:
        assert ask(first.codomain() == second.domain()) is True
        return self.MorphismType(self.morphism_category(1), first.domain(), second.codomain())

    def _equal(self, first: CategoryPoint, candidate: Any) -> Decision:
        if first in self and candidate in self:
            return ask(first.point() == candidate.point())
        morphisms = self.morphism_category(1)
        if first in morphisms and candidate in morphisms:
            return decision_and(ask(first.domain() == candidate.domain()), ask(first.codomain() == candidate.codomain()))
        return Unknown

    def __repr__(self) -> str:
        return f"Thin({self._carrier!r})"


def Thin(carrier: SetObject, order: Predicate) -> ThinCategory:
    """The thin category of the preorder ``(carrier, order)``."""
    assert carrier in Sets()
    return ThinCategory(carrier, order)


_omega: MonoDict = MonoDict()


def omega() -> ThinCategory:
    """``omega = Thin(NN)`` with the natural order: the sequential shape, constructed once (specs/functor.md, "Diagram shapes and universal constructions")."""
    from sage_categories.number_sets.positive_integers import NN, natural_order

    if NN not in _omega:
        _omega[NN] = Thin(NN, natural_order)
    return _omega[NN]
