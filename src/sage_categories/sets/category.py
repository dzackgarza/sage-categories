"""``Sets()``: the category of sets and total maps (D01, D15, D16, D17).

``Sets()`` owns arbitrary sets and arbitrary functions.  Its objects are
rule-defined (``sets/objects.py``), its elements are points ``1 -> X`` at the
classical stage ``Sets().Terminal()`` (``sets/elements.py``), and its morphisms are
total maps by rule (``sets/maps.py``).  The property subcategories ``Finite()``,
``Infinite()``, ``Countable()``, and ``Uncountable()`` own the constructors that
supply their cardinal data; ``Finite => Countable`` and ``Uncountable => Infinite``
are their recorded inclusions.  The canonical objects ``Empty()``, ``Terminal()``,
and ``Simplex(n)`` exist once by identity.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable
from typing import Any

from sage_categories.cat.category import Category
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.decisions import Decision, Unknown, decision_not
from sage_categories.kernel.predicates import ask
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import Role
from sage_categories.sets.cardinals import Cardinal
from sage_categories.sets.elements import Datum, SetPoint, points_equal
from sage_categories.sets.maps import (
    Rule,
    SetMap,
    bijective_on_finite_domain,
    injective_on_finite_domain,
    maps_equal,
    surjective_on_finite_domain,
)
from sage_categories.sets.objects import FiniteSetRole, MembershipRule, SetObject

__all__ = ["Sets", "SetsCategory"]


class FiniteSets(PropertySubcategory):
    """``Sets().Finite()``: owns construction from an explicit finite enumeration."""

    def __call__(self, *arguments: Any) -> SetObject:
        match arguments:
            case (value,) if value in self.ambient():
                refine(value, self)
                return value
            case (members,):
                return self.ObjectType(self, tuple(members))
        raise TypeError(f"{self!r} takes one set to refine or one finite enumeration")


class SetsCategory(Category):
    """The category of sets."""

    ObjectType = SetObject
    ElementType = SetPoint
    MorphismType = SetMap

    def __init__(self) -> None:
        self._canonical: dict[tuple[str, tuple[int, ...]], SetObject] = {}
        super().__init__()
        self._equality.register_handler(points_equal)
        self._equality.register_handler(maps_equal)
        countable = PropertySubcategory(self, "Countable", {}, ())
        infinite = PropertySubcategory(self, "Infinite", {}, ())
        finite = FiniteSets(self, "Finite", {Role.OBJECT: FiniteSetRole}, (countable,))
        uncountable = PropertySubcategory(self, "Uncountable", {}, (infinite,))
        # A known cardinality decides finiteness and countability (D01); established
        # placement in the complementary property decides the negation (D16).
        finite.predicate().register_handler(self._finite_by_cardinality)
        finite.predicate().register_handler(lambda ambient: False if ambient in infinite else Unknown)
        countable.predicate().register_handler(self._countable_by_cardinality)
        countable.predicate().register_handler(lambda ambient: False if ambient in uncountable else Unknown)
        infinite.predicate().register_handler(lambda ambient: decision_not(ask(ambient.is_finite())))
        uncountable.predicate().register_handler(lambda ambient: decision_not(ask(ambient.is_countable())))
        self._properties.update({"Finite": finite, "Infinite": infinite, "Countable": countable, "Uncountable": uncountable})
        morphisms = self.morphism_category(1)
        morphisms.Monomorphisms().predicate().register_handler(injective_on_finite_domain)
        morphisms.Epimorphisms().predicate().register_handler(surjective_on_finite_domain)
        morphisms.Isomorphisms().predicate().register_handler(bijective_on_finite_domain)

    # -- construction ----------------------------------------------------------------

    def __call__(self, membership_rule: MembershipRule) -> SetObject:
        """``Sets()(rule)``: the set defined by a membership rule on data, with no cardinal data."""
        return self.ObjectType(self, membership_rule, Unknown, Unknown)

    def Finite(self) -> FiniteSets:
        return self._properties["Finite"]

    def Infinite(self) -> Category:
        return self._properties["Infinite"]

    def Countable(self) -> Category:
        return self._properties["Countable"]

    def Uncountable(self) -> Category:
        return self._properties["Uncountable"]

    def _canonical_finite(self, name: str, arguments: tuple[int, ...], members: Iterable[Datum]) -> SetObject:
        if (name, arguments) not in self._canonical:
            self._canonical[name, arguments] = self.Finite()(members)
        return self._canonical[name, arguments]

    def Empty(self) -> SetObject:
        return self._canonical_finite("empty", (), ())

    def Terminal(self) -> SetObject:
        """The one-point set ``1 = {*}``, the classical stage of ``Sets()``."""
        return self._canonical_finite("terminal", (), ((),))

    def Simplex(self, dimension: int) -> SetObject:
        """``[n] = {0, ..., n}``."""
        assert dimension >= 0
        return self._canonical_finite("simplex", (dimension,), range(dimension + 1))

    def classical_stages(self) -> tuple[SetObject, ...]:
        return (self.Terminal(),)

    def element_from_defining_morphism(self, defining_morphism: SetMap) -> SetPoint:
        """The classical element whose defining morphism is the point ``1 -> X``."""
        assert defining_morphism.domain() is self.Terminal(), f"{defining_morphism!r} is not a point at the classical stage"
        return defining_morphism.codomain().category().ElementType(defining_morphism, defining_morphism._rule(()))

    # -- morphisms ----------------------------------------------------------------------

    def construct_morphism(self, domain: SetObject, codomain: SetObject, *data: Any) -> SetMap:
        """``Mor(Sets())(X, Y)(rule)`` or, with an inverse rule, an isomorphism retaining its inverse."""
        assert domain in self and codomain in self
        morphisms = self.morphism_category(1)
        match data:
            case (rule,):
                return self.MorphismType(morphisms, domain, codomain, rule, Unknown)
            case (rule, inverse_rule):
                forward = self.MorphismType(morphisms, domain, codomain, rule, Unknown)
                backward = self.MorphismType(morphisms, codomain, domain, inverse_rule, forward)
                forward._inverse = backward
                isomorphisms = morphisms.Isomorphisms()
                refine(forward, isomorphisms)
                refine(backward, isomorphisms)
                return forward
        raise TypeError("a set map is constructed from a rule, or from a rule and its inverse rule")

    def construct_identity(self, member_object: SetObject) -> SetMap:
        identity = self.MorphismType(self.morphism_category(1), member_object, member_object, lambda datum: datum, Unknown)
        identity._inverse = identity
        refine(identity, self.morphism_category(1).Isomorphisms())
        return identity

    def composite(self, second: SetMap, first: SetMap) -> SetMap:
        morphisms = self.morphism_category(1)
        assert first in morphisms and second in morphisms
        assert first.codomain() is second.domain(), f"{second!r} after {first!r} is not composable"
        composite = self.MorphismType(morphisms, first.domain(), second.codomain(), lambda datum: second._rule(first._rule(datum)), Unknown)
        if first._inverse is not Unknown and second._inverse is not Unknown:
            inverse = self.MorphismType(morphisms, second.codomain(), first.domain(), lambda datum: first._inverse._rule(second._inverse._rule(datum)), composite)
            composite._inverse = inverse
            refine(composite, morphisms.Isomorphisms())
            refine(inverse, morphisms.Isomorphisms())
        return composite

    def inverse_morphism(self, morphism: SetMap) -> SetMap:
        """The retained inverse, or the exact inverse of a bijection between finite enumerable sets."""
        if morphism._inverse is not Unknown:
            return morphism._inverse
        enumeration = morphism.domain()._enumeration
        assert enumeration is not Unknown, f"{morphism!r} retains no inverse and its domain has no chosen enumeration"
        preimages = {morphism._rule(datum): datum for datum in enumeration}
        inverse = self.MorphismType(self.morphism_category(1), morphism.codomain(), morphism.domain(), lambda datum: preimages[datum], morphism)
        morphism._inverse = inverse
        refine(inverse, self.morphism_category(1).Isomorphisms())
        return inverse

    # -- exact routes (POL-MATH-042) --------------------------------------------------

    def _finite_by_cardinality(self, ambient: SetObject) -> Decision:
        cardinality = ambient.cardinality()
        if cardinality is Unknown:
            return Unknown
        return ask(cardinality.is_finite())

    def _countable_by_cardinality(self, ambient: SetObject) -> Decision:
        cardinality = ambient.cardinality()
        if cardinality is Unknown:
            return Unknown
        return ask(cardinality.is_countable())

    def __repr__(self) -> str:
        return "Sets"


_SETS = SetsCategory()


def Sets() -> SetsCategory:
    """The category of sets."""
    return _SETS
