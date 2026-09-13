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
identities and composites are the unique comparisons. The set and the order
predicate that makes it a preorder are supplied by the caller of ``Thin``.

The sequential shape ``omega`` is ``Thin(NN, leq)`` for the natural order of ``NN``
(``specs/sets.md``, "General limits and colimits"). Its set and order are the
mathematics of ``NN``, so ``Cat`` declares that shape and the category owning them
implements it (``cat/declarations.py``, D80).

Finite presented shapes are ``FinitePresentedCategory`` (``cat/canonical.py``),
constructed uniformly by ``Cat()(labels, generators, relations)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sympy import ask as sympy_ask
from sympy import false

from sage_categories.cat.category import Category, member
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import (
    Decision,
    Predicate,
    Proposition,
    UnknownClass,
    ask,
    register_handler,
)
from sage_categories.kernel.refinement import is_placed
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = ["Discrete", "DiscreteCategory", "Thin", "ThinCategory", "carrier_comparison", "discrete_functor", "omega"]


# -- Discrete(S) ---------------------------------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class _PointObjectData:
    """The local state of a point-indexed shape object."""

    point: CategoryOfCategories.ElementType


def _initialize_point_shape_object(member_object: object, data: _PointObjectData) -> None:
    """Install the retained carrier point on one compiled point-shape object."""
    member_object._point = data.point


def _point_shape_point(member_object: object) -> CategoryOfCategories.ElementType:
    """Return the carrier point retained by one compiled point-shape object."""
    return member_object._point


def _point_shape_repr(member_object: object) -> str:
    """Represent one compiled point-shape object through its retained point and owner."""
    return f"{member_object._point!r} in {member_object.category()!r}"


def _point_shape_object_at(category: Category, point: CategoryOfCategories.ElementType):
    """Return the point-indexed object selected by ``category`` at ``point``."""
    return category(point)


def _point_shape_object_point(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    """Return the retained carrier point of a point-indexed shape object."""
    return member_object.point()


def _point_shape_identity(category: Category, member_object: CategoryOfCategories.ElementType):
    """Construct the unique identity arrow of one point-indexed shape object."""
    return category.MorphismType(member_object, member_object)


def _point_shape_construct(
    category: Category,
    point: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    """Construct the unique shape object over one carrier point."""
    carrier = category.object_set()
    assert point in carrier, f"{point!r} is not a point of {carrier!r}"
    return category.ObjectType(_PointObjectData(point))


class DiscreteCategory(Category[[], []]):
    """The discrete category on a set."""

    class ObjectType:
        """An object of ``Discrete(S)``: a point of ``S``."""

        __init__ = _initialize_point_shape_object
        point = _point_shape_point
        __repr__ = _point_shape_repr

    class MorphismType:
        """The only morphisms of a discrete category: identities."""

        def __repr__(self) -> str:
            return f"identity of {self.domain()!r}"

    class ElementType:
        """A generalized element of a point; no local operation."""

    def __init__(self, index_set: CategoryOfCategories.ElementType) -> None:
        self._index_set = index_set
        super().__init__()
        register_handler(self._equality, self._equal)

    def index_set(self) -> CategoryOfCategories.ElementType:
        return self._index_set

    def is_discrete(self) -> bool:
        return True

    # The objects are the points of ``S`` and the morphisms their identities (specs/functor.md, "Diagram shapes and universal constructions").

    def object_set(self) -> CategoryOfCategories.ElementType:
        return self.index_set()

    def object_at(self, point: CategoryOfCategories.ElementType) -> DiscreteCategory.ObjectType:
        return _point_shape_object_at(self, point)

    def object_point(self, member_object: DiscreteCategory.ObjectType) -> CategoryOfCategories.ElementType:
        return _point_shape_object_point(member_object)

    def _chosen_morphism_set(self) -> CategoryOfCategories.ElementType | UnknownClass:
        return self.index_set()

    def morphism_at(self, point: CategoryOfCategories.ElementType) -> DiscreteCategory.MorphismType:
        vertex = self.object_at(point)
        return self.morphism_category(1)(vertex, vertex).one()

    def generating_morphisms(self) -> tuple[DiscreteCategory.MorphismType, ...]:
        """No morphism beyond the identities: the empty generating family."""
        return ()

    @cached_method(key=lambda self, point: identity_key(point))
    def __call__(self, point: CategoryOfCategories.ElementType) -> DiscreteCategory.ObjectType:
        """The object of ``Discrete(S)`` at a point of ``S``, one object per retained point."""
        return _point_shape_construct(self, point)

    def construct_morphism(self, domain: DiscreteCategory.ObjectType, codomain: DiscreteCategory.ObjectType) -> DiscreteCategory.MorphismType:
        """``Mor(Discrete(S))(x, y)()``: the identity, which exists exactly when ``x == y``."""
        assert ask(domain == codomain), f"{self!r} has no morphism {domain!r} -> {codomain!r}"
        return self.MorphismType(domain, codomain)

    def construct_identity(self, member_object: DiscreteCategory.ObjectType) -> DiscreteCategory.MorphismType:
        return _point_shape_identity(self, member_object)

    def composite(self, second: DiscreteCategory.MorphismType, first: DiscreteCategory.MorphismType) -> DiscreteCategory.MorphismType:
        return _thin_composite(self, second, first)

    def _equal(
        self,
        first: CategoryOfCategories.ElementType,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        """Objects are equal when their points are; morphisms when their domains are."""
        if first._is_object() and candidate._is_object() and is_placed(first, self) and is_placed(candidate, self):
            return sympy_ask(first.point() == candidate.point(), assumptions)
        morphisms = self.morphism_category(1)
        if first._is_morphism() and candidate._is_morphism() and is_placed(first, morphisms) and is_placed(candidate, morphisms):
            return sympy_ask(first.domain() == candidate.domain(), assumptions)
        return None

    def __repr__(self) -> str:
        return f"Discrete({self._index_set!r})"


def _thin_composite(
    category: Category,
    second: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """Compose in a thin category: compatible endpoints determine the unique arrow."""
    assert ask(first.codomain() == second.domain())
    return category.MorphismType(first.domain(), second.codomain())


@cached_function(key=identity_key)
def _discrete_on_object(index_set: CategoryOfCategories.ElementType) -> DiscreteCategory:
    return DiscreteCategory(index_set)


@cached_function(key=identity_key)
def _discrete_on_morphism(set_map: MorphismCategory.ObjectType) -> Functor:
    source, target = _discrete_on_object(set_map.domain()), _discrete_on_object(set_map.codomain())
    return Fun(source, target)(
        lambda vertex: target(set_map(vertex.point())),
        lambda identity: target.morphism_at(set_map(identity.domain().point())),
    )


# The functor ``Discrete: Sets() -> Cat()``, retained once; ``Discrete(S)`` is its
# object action and ``Discrete(f)`` its morphism action (Mathlib
# ``CategoryTheory.Discrete.functor`` for the action on maps; inspected 2026-08-26).
def discrete_functor(sets: Category) -> Functor:
    """Discretization for a supplied category of sets and total functions."""
    return Fun(sets, Cat())(_discrete_on_object, _discrete_on_morphism)


Discrete: Functor = discrete_functor(Sets)


class DiscreteObjectCategory(DiscreteCategory):
    """A set-valued object with its own discrete category of points.

    The discrete realization and its comparison follow the category-of-elements
    fiber of a set-valued functor (Mathlib CategoryTheory.Elements).
    """

    class ObjectType:
        def _deciding_category(self) -> Category:
            return self.parent().category()

    class ElementType:
        pass

    class MorphismType:
        pass

    def __call__(self, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        assert point.parent() is self
        return point

    def object_at(self, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        assert point.parent() is self._index_set
        return self.point(point.datum())

    def object_point(self, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        assert point.parent() is self
        return self._index_set.point(point.datum())

    @cached_method
    def point_comparison(self) -> Functor:
        """The retained comparison with the discrete selected carrier."""
        target = Discrete(self._index_set)
        return Fun(self, target)(
            lambda point: target(self.object_point(point)),
            lambda identity: target.morphism_at(self.object_point(identity.domain())),
        )


def realize_discrete_object(value: CategoryOfCategories.ElementType) -> None:
    """Construct a discrete category on the same retained set-valued object."""
    from sage_categories.kernel.construction import realize_object

    realize_object(value, DiscreteObjectCategory)


def carrier_comparison(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
) -> Proposition | None:
    """``U(x) == U(y)``: equality of two points of one object, read in its carrier.

    A category of structured objects is concrete: its forgetful functor ``U`` to the
    carrier is faithful, hence injective on hom sets, so two points ``x, y: 1 -> X`` are
    equal exactly when ``U(x)`` and ``U(y)`` are.  The equality predicate of ``X`` is
    therefore the pullback of the carrier's along ``U``, and this states that pullback
    once for every concrete category rather than in each of them.

    The proposition is the carrier's own, so the carrier decides it: a quotient or
    presented carrier normalizes its data before answering, and no comparison of raw data
    happens here.  ``None`` where there is no reading to take: values that are not both
    points of one realized object, and an object that is its own carrier, whose transport
    is the identity and states nothing new.  Points of two different objects are two
    values, so their comparison is decided false.
    """
    owner, other = first.category(), second.category()
    if not (isinstance(owner, DiscreteObjectCategory) and isinstance(other, DiscreteObjectCategory)):
        return None
    if owner is not other:
        return false
    transported = owner.object_point(first)
    return None if transported is first else transported == owner.object_point(second)


# -- Thin(P, leq) --------------------------------------------------------------------


# ``comparable(f, T)``: the endpoints of the comparison ``f`` of ``T`` satisfy ``T``'s order.
class _ComparablePredicate(Predicate):
    name = "comparable"


comparable = _ComparablePredicate()


def _comparable_by_order(
    candidate: CategoryOfCategories.ElementType,
    thin: Category,
    assumptions: Proposition,
) -> bool | None:
    if not is_placed(candidate, thin.morphism_category(1)):
        return None
    return sympy_ask(
        thin.order()(candidate.domain().point(), candidate.codomain().point()),
        assumptions,
    )


register_handler(comparable, _comparable_by_order)


class ThinMorphisms(MorphismCategory[[], []]):
    """``Mor(Thin(P, leq))``: a comparison is a member when its order proposition holds."""

    class ObjectType:
        """A comparison ``x <= y`` of ``Thin(P, leq)``, which is a morphism of it."""

    class ElementType:
        """A generalized element of a comparison: its identity 2-morphism, a thin category being a 1-category."""

    class MorphismType:
        """The identity 2-morphism of a comparison: a thin category has no other 2-morphism."""

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return member(candidate, self) & comparable(candidate, self._base)


class ThinCategory(Category[[], []]):
    """The thin category of a preorder ``(P, leq)``."""

    class ObjectType:
        """An object of ``Thin(P, leq)``: a point of ``P``."""

        __init__ = _initialize_point_shape_object
        point = _point_shape_point
        __repr__ = _point_shape_repr

    class MorphismType:
        """The unique morphism ``x -> y`` of a thin category, present when ``x <= y``."""

        def __repr__(self) -> str:
            return f"{self.domain()!r} <= {self.codomain()!r}"

    class ElementType:
        """A generalized element of a point; no local operation."""

    def __init__(self, carrier: CategoryOfCategories.ElementType, order: Predicate) -> None:
        self._carrier = carrier
        self._order = order
        super().__init__()
        register_handler(self._equality, self._equal)

    def carrier(self) -> CategoryOfCategories.ElementType:
        return self._carrier

    def order(self) -> Predicate:
        return self._order

    def morphism_category_type(self) -> type[ThinMorphisms]:
        return ThinMorphisms

    # The objects are the points of ``P``; no finite family of comparisons is chosen.

    def object_set(self) -> CategoryOfCategories.ElementType:
        return self.carrier()

    def object_at(self, point: CategoryOfCategories.ElementType) -> ThinCategory.ObjectType:
        return _point_shape_object_at(self, point)

    def object_point(self, member_object: ThinCategory.ObjectType) -> CategoryOfCategories.ElementType:
        return _point_shape_object_point(member_object)

    @cached_method(key=lambda self, point: identity_key(point))
    def __call__(self, point: CategoryOfCategories.ElementType) -> ThinCategory.ObjectType:
        """The object at a point of ``P``, one object per retained point."""
        return _point_shape_construct(self, point)

    def construct_morphism(self, domain: ThinCategory.ObjectType, codomain: ThinCategory.ObjectType) -> ThinCategory.MorphismType:
        """``Mor(Thin)(x, y)()``: the comparison ``x <= y``; rejected only when the order decides against it."""
        assert ask(self._order(domain.point(), codomain.point())) is not False, f"{domain!r} <= {codomain!r} is false"
        return self.MorphismType(domain, codomain)

    def construct_identity(self, member_object: ThinCategory.ObjectType) -> ThinCategory.MorphismType:
        return _point_shape_identity(self, member_object)

    def composite(self, second: ThinCategory.MorphismType, first: ThinCategory.MorphismType) -> ThinCategory.MorphismType:
        return _thin_composite(self, second, first)

    def _chosen_hom_inhabited(self, hom_category: Category) -> Decision:
        domain = hom_category.domain()
        codomain = hom_category.codomain()
        return ask(self._order(domain.point(), codomain.point()))

    def _equal(
        self,
        first: CategoryOfCategories.ElementType,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        if first._is_object() and candidate._is_object() and is_placed(first, self) and is_placed(candidate, self):
            return sympy_ask(first.point() == candidate.point(), assumptions)
        morphisms = self.morphism_category(1)
        if first._is_morphism() and candidate._is_morphism() and is_placed(first, morphisms) and is_placed(candidate, morphisms):
            return sympy_ask(
                (first.domain() == candidate.domain()) & (first.codomain() == candidate.codomain()),
                assumptions,
            )
        return None

    def __repr__(self) -> str:
        return f"Thin({self._carrier!r})"


def Thin(carrier: CategoryOfCategories.ElementType, order: Predicate) -> ThinCategory:
    """Return the thin category of the supplied set and order predicate."""
    assert carrier in Sets or carrier in Cat()
    return ThinCategory(carrier, order)


def omega() -> Category:
    """``omega = Thin(NN, natural_order)``: the sequential shape (specs/functor.md, "Diagram shapes and universal constructions").

    Its set and order are the mathematics of ``NN``, so ``Cat`` declares this
    shape and the category that owns them implements it (D80).  The kernel owns ``Thin``,
    which is the construction, and names the one shape it is applied to here.
    """
    from sage_categories.cat.declarations import omega as declared

    return declared
