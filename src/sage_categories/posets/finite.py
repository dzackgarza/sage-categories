"""``FinitePosets()``: the finite posets and their finite order algorithms (``specs/ordered-sets.md``, "Finite-poset API").

``FinitePosets()`` is the property subcategory of ``Posets()`` by finiteness of the
underlying set (``specs/ordered-sets.md``, "Category and role surface").  It is not a
narrowing of ``Posets()`` by ``Sets().Finite()``: a poset is never placed in ``Sets()``
or a subcategory of it, and POL-CAT-084 derives a narrowing only along a selected
inclusion.  Its two selected functors are the inclusion into ``Posets()`` and the
restriction of ``U`` to ``Sets().Finite()``, whose object action returns the very same
retained underlying set; both routes to ``Sets()`` therefore return one value by
identity (``specs/resolution.md``, "Finite-rank free modules over finite fields").  Its
trusted constructor refines the underlying set through ``Sets().Finite()`` and the poset
through this category (POL-CAT-069); a poset on a finite set enters here at
construction (POL-CAT-081); its predicate is decided by the inherited ``P.is_finite()``,
the finiteness proposition of ``U(P)``.

The finite operations lower the poset to a Sage finite poset once
(``_finite_poset_sage.py``, POL-LAYOUT-020) and reconstruct owned results
(POL-LEAF-044): elements as classical elements, collections as sub-posets, counts as
cardinals, properties as placements.  Bottom, top, and rank belong to the property
subcategories that guarantee them (POL-API-019): ``WithBottom()``, ``WithTop()``,
``Ranked()``; ``Graded()`` implies ``Ranked()`` (Sage ``is_graded``: a graded poset is
ranked with all maximal chains of one length; inspected 2026-08-27).
"""

from __future__ import annotations

from collections.abc import Callable

from sage.combinat.posets.posets import FinitePoset as SagePoset

import sage_categories.posets.category as _posets
from sage_categories.cat.category import Category
from sage_categories.cat.diagrams import sequence_position
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.shapes import Discrete
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import AppliedPredicate, ask
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import CategoryPoint, ObjectOfCategory, Role
from sage_categories.posets import _finite_poset_sage as engine
from sage_categories.posets.category import Poset, PosetElement
from sage_categories.sets.cardinals import Cardinal, CardinalObject
from sage_categories.sets.category import Sets
from sage_categories.sets.maps import Rule

__all__ = ["FinitePosetRole", "FinitePosetsCategory", "GradedRole", "RankedRole", "WithBottomRole", "WithTopRole"]


class FinitePosetRole(ObjectOfCategory):
    """The local object role of ``FinitePosets()``: the finite order algorithms."""

    def has_bottom(self) -> AppliedPredicate:
        return _posets.Posets().Finite().WithBottom().predicate()(self)

    def has_top(self) -> AppliedPredicate:
        return _posets.Posets().Finite().WithTop().predicate()(self)

    def is_ranked(self) -> AppliedPredicate:
        return _posets.Posets().Finite().Ranked().predicate()(self)

    def is_graded(self) -> AppliedPredicate:
        return _posets.Posets().Finite().Graded().predicate()(self)

    def height(self) -> CardinalObject:
        """The number of elements of a longest chain."""
        return Cardinal()(engine.count(engine.sage_poset(self).height()))

    def width(self) -> CardinalObject:
        """The number of elements of a largest antichain."""
        return Cardinal()(engine.count(engine.sage_poset(self).width()))

    def covers(self, lower: PosetElement, upper: PosetElement) -> Decision:
        """Whether ``upper`` covers ``lower``: ``lower < upper`` with nothing between."""
        return engine.sage_poset(self).covers(engine.datum(self, lower), engine.datum(self, upper))

    def lower_covers(self, member: PosetElement) -> Poset:
        return self.sub_poset(engine.selecting(engine.sage_poset(self).lower_covers(engine.datum(self, member))))

    def upper_covers(self, member: PosetElement) -> Poset:
        return self.sub_poset(engine.selecting(engine.sage_poset(self).upper_covers(engine.datum(self, member))))

    def minimal_elements(self) -> Poset:
        return self.sub_poset(engine.selecting(engine.sage_poset(self).minimal_elements()))

    def maximal_elements(self) -> Poset:
        return self.sub_poset(engine.selecting(engine.sage_poset(self).maximal_elements()))

    def common_lower_covers(self, members: Poset) -> Poset:
        """The sub-poset of elements covered by every element of the sub-poset ``members``."""
        return self.sub_poset(engine.selecting(engine.sage_poset(self).common_lower_covers(engine.data(self, members))))

    def common_upper_covers(self, members: Poset) -> Poset:
        """The sub-poset of elements covering every element of the sub-poset ``members``."""
        return self.sub_poset(engine.selecting(engine.sage_poset(self).common_upper_covers(engine.data(self, members))))

    def open_interval(self, lower: PosetElement, upper: PosetElement) -> Poset:
        """``{z : lower < z < upper}`` with the induced order."""
        return self.sub_poset(engine.selecting(engine.sage_poset(self).open_interval(engine.datum(self, lower), engine.datum(self, upper))))

    def closed_interval(self, lower: PosetElement, upper: PosetElement) -> Poset:
        """``{z : lower <= z <= upper}`` with the induced order."""
        return self.sub_poset(engine.selecting(engine.sage_poset(self).closed_interval(engine.datum(self, lower), engine.datum(self, upper))))

    def principal_order_ideal(self, member: PosetElement) -> Poset:
        """``{z : z <= member}`` with the induced order."""
        return self.sub_poset(engine.selecting(engine.sage_poset(self).order_ideal((engine.datum(self, member),))))

    def principal_order_filter(self, member: PosetElement) -> Poset:
        """``{z : member <= z}`` with the induced order."""
        return self.sub_poset(engine.selecting(engine.sage_poset(self).order_filter((engine.datum(self, member),))))

    def order_ideal(self, members: Poset) -> Poset:
        """The down-closure of the sub-poset ``members``, with the induced order."""
        return self.sub_poset(engine.selecting(engine.sage_poset(self).order_ideal(engine.data(self, members))))

    def order_filter(self, members: Poset) -> Poset:
        """The up-closure of the sub-poset ``members``, with the induced order."""
        return self.sub_poset(engine.selecting(engine.sage_poset(self).order_filter(engine.data(self, members))))

    def is_chain_of_poset(self, members: Poset) -> Decision:
        """Whether the elements of the sub-poset ``members`` are pairwise comparable."""
        return bool(engine.sage_poset(self).is_chain_of_poset(engine.data(self, members)))

    def is_antichain_of_poset(self, members: Poset) -> Decision:
        """Whether the elements of the sub-poset ``members`` are pairwise incomparable."""
        return bool(engine.sage_poset(self).is_antichain_of_poset(engine.data(self, members)))

    def linear_extension(self) -> Poset:
        """A total order on ``U(P)`` extending the order of ``P``.

        Sage ``FinitePoset.linear_extension`` lists the elements in an order compatible with
        ``P`` (inspected 2026-08-27); the order of positions in that list is linear.
        """
        posets = _posets.Posets()
        positions = {datum: position for position, datum in enumerate(engine.sage_poset(self).linear_extension())}
        carrier = posets.underlying_set_functor().on_object(self)
        extension = (carrier * carrier).subset_from(lambda pair: positions[pair(0)] <= positions[pair(1)])
        return posets.TotallyOrdered()(posets._construct(carrier, extension))


class WithBottomRole(ObjectOfCategory):
    """The local object role of ``FinitePosets().WithBottom()``."""

    def bottom(self) -> PosetElement:
        return engine.element(self, engine.sage_poset(self).bottom())


class WithTopRole(ObjectOfCategory):
    """The local object role of ``FinitePosets().WithTop()``."""

    def top(self) -> PosetElement:
        return engine.element(self, engine.sage_poset(self).top())


class RankedRole(ObjectOfCategory):
    """The local object role of ``FinitePosets().Ranked()``: the rank function."""

    def rank(self) -> CardinalObject:
        """The rank of the poset: the rank of its top elements."""
        return Cardinal()(engine.count(engine.sage_poset(self).rank()))

    def rank_of_element(self, member: PosetElement) -> CardinalObject:
        return Cardinal()(engine.count(engine.sage_poset(self).rank(engine.datum(self, member))))

    def level_sets(self) -> Functor:
        """The rank levels ``P_0, ..., P_r`` as a diagram ``Discrete([r]) -> Posets()`` of sub-posets.

        On a ranked poset the level of an element is its rank: Sage ``FinitePoset.level_sets``
        groups elements by the maximal number of covers from a minimal element, and
        ``FinitePoset.rank_function`` is normalized to ``0`` on the minimal elements of each
        component (inspected 2026-08-27).
        """
        levels = tuple(self.sub_poset(engine.selecting(level)) for level in engine.sage_poset(self).level_sets())
        return Fun(Discrete(Sets().Simplex(len(levels) - 1)), _posets.Posets()).from_object_rule(lambda vertex: levels[sequence_position(vertex)])


class GradedRole(ObjectOfCategory):
    """The local object role of ``FinitePosets().Graded()``; grading adds no operation beyond rank."""


def _finite_by_underlying_set(poset: CategoryPoint) -> Decision:
    """Finiteness of a poset is finiteness of ``U(P)``, asked through the inherited ``is_finite()``."""
    if poset not in _posets.Posets():
        return Unknown
    return ask(poset.is_finite())


def _decided_by(query: Callable[[SagePoset], bool]) -> Callable[[CategoryPoint], Decision]:
    """The exact handler deciding a property of a finite poset by a Sage finite-poset query."""

    def decide(poset: CategoryPoint) -> Decision:
        if poset not in _posets.Posets().Finite():
            return Unknown
        return bool(query(engine.sage_poset(poset)))

    return decide


class FinitePosetsCategory(PropertySubcategory[[Rule], []]):
    """``Posets().Finite()``: finite posets, with the restriction of ``U`` to finite sets selected."""

    def __init__(self, ambient: Category[[Rule], []], name: str, roles: dict[Role, type], implications: tuple[Category, ...]) -> None:
        self._functors: dict[str, Functor] = {}
        super().__init__(ambient, name, roles, implications)
        self.predicate().register_handler(_finite_by_underlying_set)
        self._with_bottom = PropertySubcategory(self, "WithBottom", {Role.OBJECT: WithBottomRole}, ())
        self._with_top = PropertySubcategory(self, "WithTop", {Role.OBJECT: WithTopRole}, ())
        self._ranked = PropertySubcategory(self, "Ranked", {Role.OBJECT: RankedRole}, ())
        self._graded = PropertySubcategory(self, "Graded", {Role.OBJECT: GradedRole}, (self._ranked,))
        self._with_bottom.predicate().register_handler(_decided_by(lambda finite_poset: finite_poset.has_bottom()))
        self._with_top.predicate().register_handler(_decided_by(lambda finite_poset: finite_poset.has_top()))
        self._ranked.predicate().register_handler(_decided_by(lambda finite_poset: finite_poset.is_ranked()))
        self._graded.predicate().register_handler(_decided_by(lambda finite_poset: finite_poset.is_graded()))

    def structure_functors(self) -> tuple[Functor, ...]:
        """The inclusion into ``Posets()``, then ``U`` restricted to ``Sets().Finite()``."""
        if "underlying_finite_set" not in self._functors:
            underlying = self._ambient.underlying_set_functor()
            self._functors["underlying_finite_set"] = Fun(self, Sets().Finite()).Faithful()(underlying.on_object, underlying.on_morphism)
        return (*super().structure_functors(), self._functors["underlying_finite_set"])

    def __call__(self, poset: Poset) -> Poset:
        """The trusted constructor: the underlying set is finite, so it enters ``Sets().Finite()`` with the poset here."""
        assert poset in self._ambient, f"{poset!r} is not an object of {self._ambient!r}"
        Sets().Finite()(self._ambient.underlying_set_functor().on_object(poset))
        refine(poset, self)
        return poset

    def TotallyOrdered(self) -> Category[[Rule], []]:
        """``FinitePosets().TotallyOrdered()``: the narrowing of ``Posets().TotallyOrdered()`` to finite posets (POL-CAT-084)."""
        return self.property_subcategory(self._ambient.TotallyOrdered())

    def WithBottom(self) -> Category[[Rule], []]:
        return self._with_bottom

    def WithTop(self) -> Category[[Rule], []]:
        return self._with_top

    def Ranked(self) -> Category[[Rule], []]:
        return self._ranked

    def Graded(self) -> Category[[Rule], []]:
        return self._graded
