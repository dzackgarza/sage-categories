"""Diagram shapes supplied by the kernel: ``Discrete(S)`` and ``Thin(P, leq)`` (POL-SET-013, POL-SET-014).

``Discrete`` is a functor ``Sets() -> Cat()`` retained once.  ``Discrete(S)`` is the
discrete category on the set ``S``: its objects are the points of ``S``
and its morphisms are identities only (Mathlib ``CategoryTheory.Discrete`` and
``CategoryTheory.discreteCategory``; inspected 2026-08-26).  No enumeration of
``S`` occurs: an object ``Discrete(S)(x)`` is constructed from a point ``x`` whose
membership in ``S`` is asserted, and two objects are equal exactly when their
points are.  A set map ``f: S -> T`` is sent to the functor ``Discrete(S) ->
Discrete(T)`` acting on points by ``f``.

``Thin(P, leq)`` is the thin category of a preorder given as a set ``P`` with an
order predicate ``leq``: objects are the points of ``P`` and there is at most one
morphism ``x -> y``, which exists when ``ask(leq(x, y))`` holds (Mathlib
``Preorder.smallCategory`` and ``Preorder.subsingleton_hom``; inspected
2026-08-26).  The writer asserts reflexivity and transitivity (POL-MATH-037):
identities and composites are the unique comparisons.  The carrier and the order
predicate that makes it a preorder are supplied by the caller of ``Thin``.

The sequential shape ``omega`` is ``Thin(NN, leq)`` for the natural order of ``NN``
(``specs/sets.md``, "General limits and colimits").  Its carrier and its order are the
mathematics of ``NN``, so ``Cat`` declares that shape and the category owning them
implements it (``cat/declarations.py``, D80).

Finite presented shapes are ``FinitePresentedCategory`` (``cat/canonical.py``),
constructed uniformly by ``Cat()(labels, generators, relations)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory

__all__ = ["Discrete", "DiscreteCategory", "Thin", "ThinCategory", "index_set_of", "is_discrete", "omega"]


# -- Discrete(S) ---------------------------------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class DiscreteObjectData:
    """The local state introduced by a discrete-category object."""

    point: ElementOfObject


class DiscreteCategory(Category[[], []]):
    """The discrete category on a set."""

    class ObjectType(ObjectOfCategory):
        """An object of ``Discrete(S)``: a point of ``S``."""

        def __init__(self, data: DiscreteObjectData) -> None:
            self._point = data.point
            super().__init__()

        def point(self) -> ElementOfObject:
            """The point of the index set that this object is."""
            return self._point

        def __repr__(self) -> str:
            return f"{self._point!r} in {self.category()!r}"

    class MorphismType(MorphismOfCategory):
        """The only morphisms of a discrete category: identities."""

        def __repr__(self) -> str:
            return f"identity of {self.domain()!r}"

    class ElementType(ElementOfObject):
        """A generalized element of a point; no local operation."""

    def __init__(self, index_set: ObjectOfCategory) -> None:
        self._index_set = index_set
        self._objects: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(self._equal)

    def index_set(self) -> ObjectOfCategory:
        return self._index_set

    # The objects are the points of ``S`` and the morphisms their identities (specs/functor.md, "Diagram shapes and universal constructions").

    def object_set(self) -> ObjectOfCategory:
        return self._index_set

    def object_at(self, point: ElementOfObject) -> DiscreteCategory.ObjectType:
        return self(point)

    def object_point(self, member_object: DiscreteCategory.ObjectType) -> ElementOfObject:
        return member_object.point()

    def _chosen_morphism_set(self) -> ObjectOfCategory | UnknownClass:
        return self._index_set

    def morphism_at(self, point: ElementOfObject) -> DiscreteCategory.MorphismType:
        return self(point).identity()

    def generating_morphisms(self) -> tuple[DiscreteCategory.MorphismType, ...]:
        """No morphism beyond the identities: the empty generating family."""
        return ()

    def __call__(self, point: ElementOfObject) -> DiscreteCategory.ObjectType:
        """The object of ``Discrete(S)`` at a point of ``S``, one object per retained point."""
        assert point in self._index_set, f"{point!r} is not a point of {self._index_set!r}"
        if point not in self._objects:
            self._objects[point] = self.ObjectType(category=self, data=DiscreteObjectData(point))
        return self._objects[point]

    def construct_morphism(self, domain: DiscreteCategory.ObjectType, codomain: DiscreteCategory.ObjectType) -> DiscreteCategory.MorphismType:
        """``Mor(Discrete(S))(x, y)()``: the identity, which exists exactly when ``x == y``."""
        assert ask(domain == codomain), f"{self!r} has no morphism {domain!r} -> {codomain!r}"
        return self.MorphismType(self.morphism_category(1), domain, codomain)

    def construct_identity(self, member_object: DiscreteCategory.ObjectType) -> DiscreteCategory.MorphismType:
        return self.MorphismType(self.morphism_category(1), member_object, member_object)

    def composite(self, second: DiscreteCategory.MorphismType, first: DiscreteCategory.MorphismType) -> DiscreteCategory.MorphismType:
        assert ask(first.codomain() == second.domain())
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


def _discrete_on_object(index_set: ObjectOfCategory) -> DiscreteCategory:
    if index_set not in _discrete_categories:
        shape = DiscreteCategory(index_set)
        _discrete_categories[index_set] = shape
        _index_sets[shape] = index_set
    return _discrete_categories[index_set]


def _discrete_on_morphism(set_map: MorphismOfCategory) -> Functor:
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
Discrete: Functor = Fun(Sets, Cat())(_discrete_on_object, _discrete_on_morphism)


def is_discrete(shape: Category) -> bool:
    """Whether ``shape`` is a retained image ``Discrete(S)``."""
    return shape in _index_sets


def index_set_of(shape: Category) -> ObjectOfCategory:
    """The set ``S`` with ``shape is Discrete(S)``."""
    assert is_discrete(shape), f"{shape!r} is not Discrete(S) for a set S"
    return _index_sets[shape]


# -- Thin(P, leq) --------------------------------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class ThinObjectData:
    """The local state introduced by a thin-category object."""

    point: ElementOfObject


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

    class ObjectType(ObjectOfCategory):
        """An object of ``Thin(P, leq)``: a point of ``P``."""

        def __init__(self, data: ThinObjectData) -> None:
            self._point = data.point
            super().__init__()

        def point(self) -> ElementOfObject:
            return self._point

        def __repr__(self) -> str:
            return f"{self._point!r} in {self.category()!r}"

    class MorphismType(MorphismOfCategory):
        """The unique morphism ``x -> y`` of a thin category, present when ``x <= y``."""

        def __repr__(self) -> str:
            return f"{self.domain()!r} <= {self.codomain()!r}"

    class ElementType(ElementOfObject):
        """A generalized element of a point; no local operation."""

    def __init__(self, carrier: ObjectOfCategory, order: Predicate) -> None:
        assert order.arity() == 2
        self._carrier = carrier
        self._order = order
        self._objects: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(self._equal)

    def carrier(self) -> ObjectOfCategory:
        return self._carrier

    def order(self) -> Predicate:
        return self._order

    def morphism_category_type(self) -> type[ThinMorphisms]:
        return ThinMorphisms

    # The objects are the points of ``P``; no finite family of comparisons is chosen.

    def object_set(self) -> ObjectOfCategory:
        return self._carrier

    def object_at(self, point: ElementOfObject) -> ThinCategory.ObjectType:
        return self(point)

    def object_point(self, member_object: ThinCategory.ObjectType) -> ElementOfObject:
        return member_object.point()

    def __call__(self, point: ElementOfObject) -> ThinCategory.ObjectType:
        """The object at a point of ``P``, one object per retained point."""
        assert point in self._carrier, f"{point!r} is not a point of {self._carrier!r}"
        if point not in self._objects:
            self._objects[point] = self.ObjectType(category=self, data=ThinObjectData(point))
        return self._objects[point]

    def construct_morphism(self, domain: ThinCategory.ObjectType, codomain: ThinCategory.ObjectType) -> ThinCategory.MorphismType:
        """``Mor(Thin)(x, y)()``: the comparison ``x <= y``; rejected only when the order decides against it."""
        assert ask(self._order(domain.point(), codomain.point())) is not False, f"{domain!r} <= {codomain!r} is false"
        return self.MorphismType(self.morphism_category(1), domain, codomain)

    def construct_identity(self, member_object: ThinCategory.ObjectType) -> ThinCategory.MorphismType:
        return self.MorphismType(self.morphism_category(1), member_object, member_object)

    def composite(self, second: ThinCategory.MorphismType, first: ThinCategory.MorphismType) -> ThinCategory.MorphismType:
        assert ask(first.codomain() == second.domain())
        return self.MorphismType(self.morphism_category(1), first.domain(), second.codomain())

    def _equal(self, first: CategoryPoint, candidate: Any) -> Decision:
        if first in self and candidate in self:
            return ask(first.point() == candidate.point())
        morphisms = self.morphism_category(1)
        if first in morphisms and candidate in morphisms:
            return ask((first.domain() == candidate.domain()) & (first.codomain() == candidate.codomain()))
        return Unknown

    def __repr__(self) -> str:
        return f"Thin({self._carrier!r})"


def Thin(carrier: ObjectOfCategory, order: Predicate) -> ThinCategory:
    """The thin category of the preorder ``(carrier, order)``."""
    assert carrier in Sets
    return ThinCategory(carrier, order)


def omega() -> Category:
    """``omega = Thin(NN, natural_order)``: the sequential shape (specs/functor.md, "Diagram shapes and universal constructions").

    Its carrier and its order are the mathematics of ``NN``, so ``Cat`` declares this
    shape and the category that owns them implements it (D80).  The kernel owns ``Thin``,
    which is the construction, and names the one shape it is applied to here.
    """
    from sage_categories.cat.declarations import omega as declared

    return declared
