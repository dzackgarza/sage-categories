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
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.properties import PropertySubcategory
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
        with_bottom = PropertySubcategory(self, "WithBottom", {Role.OBJECT: WithBottomRole}, ())
        with_top = PropertySubcategory(self, "WithTop", {Role.OBJECT: WithTopRole}, ())
        ranked = PropertySubcategory(self, "Ranked", {Role.OBJECT: RankedRole}, ())
        graded = PropertySubcategory(self, "Graded", {Role.OBJECT: GradedRole}, (ranked,))
        with_bottom.predicate().register_handler(_decided_by(lambda finite_poset: finite_poset.has_bottom()))
        with_top.predicate().register_handler(_decided_by(lambda finite_poset: finite_poset.has_top()))
        ranked.predicate().register_handler(_decided_by(lambda finite_poset: finite_poset.is_ranked()))
        graded.predicate().register_handler(_decided_by(lambda finite_poset: finite_poset.is_graded()))
        self._properties.update({"WithBottom": with_bottom, "WithTop": with_top, "Ranked": ranked, "Graded": graded})

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

    def WithBottom(self) -> Category[[Rule], []]:
        return self._properties["WithBottom"]

    def WithTop(self) -> Category[[Rule], []]:
        return self._properties["WithTop"]

    def Ranked(self) -> Category[[Rule], []]:
        return self._properties["Ranked"]

    def Graded(self) -> Category[[Rule], []]:
        return self._properties["Graded"]
