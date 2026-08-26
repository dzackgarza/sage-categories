"""``Sets()``: the category of sets and total maps (D01, D15, D16, D17).

``Sets()`` owns arbitrary sets and arbitrary functions.  Its objects are
rule-defined (``sets/objects.py``), its elements are points ``1 -> X`` at the
classical stage ``Sets().Terminal()`` (``sets/elements.py``), and its morphisms are
total maps by rule (``sets/maps.py``).  The property subcategories ``Finite()``,
``Infinite()``, ``Countable()``, and ``Uncountable()`` own the constructors that
supply their cardinal data; ``Finite => Countable`` and ``Uncountable => Infinite``
are their recorded inclusions.  The canonical objects ``Empty()``, ``Terminal()``,
and ``Simplex(n)`` exist once by identity.

Retained construction data, each keyed by identity at its owner: the chosen
enumeration of a finite set at ``Sets().Finite()``; the inverse of an isomorphism
at ``Sets()`` (``inverse_morphism``).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, overload

from sage.structure.coerce_dict import MonoDict

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

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor

__all__ = ["Sets", "SetsCategory"]


class FiniteSets(PropertySubcategory[[Rule], []]):
    """``Sets().Finite()``: owns construction from an explicit finite enumeration and retains it."""

    def __init__(self, ambient: Category[[Rule], []], name: str, roles: dict[Role, type], implications: tuple[Category, ...]) -> None:
        self._enumerations: MonoDict = MonoDict()
        super().__init__(ambient, name, roles, implications)

    def __call__(self, members: SetObject | Iterable[Datum]) -> SetObject:
        """Refine a set of ``Sets()``, or construct the finite set with the given enumeration."""
        if members in self.ambient():
            refine(members, self)
            return members
        enumeration = tuple(members)
        finite_set = self.ObjectType(self, enumeration)
        self._enumerations[finite_set] = enumeration
        return finite_set

    def has_chosen_enumeration(self, finite_set: SetObject) -> bool:
        return finite_set in self._enumerations

    def chosen_enumeration(self, finite_set: SetObject) -> tuple[Datum, ...]:
        """The enumeration this constructor retained for ``finite_set``."""
        assert finite_set in self._enumerations, f"{finite_set!r} has no chosen enumeration"
        return self._enumerations[finite_set]


class SetsCategory(Category[[Rule], []]):
    """The category of sets."""

    ObjectType = SetObject
    ElementType = SetPoint
    MorphismType = SetMap

    def __init__(self) -> None:
        self._canonical: dict[tuple[str, tuple[int, ...]], SetObject] = {}
        self._inverses: MonoDict = MonoDict()
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
        return self.ObjectType(self, membership_rule, Unknown)

    def Finite(self) -> FiniteSets:
        return self._properties["Finite"]

    def Infinite(self) -> Category[[Rule], []]:
        return self._properties["Infinite"]

    def Countable(self) -> Category[[Rule], []]:
        return self._properties["Countable"]

    def Uncountable(self) -> Category[[Rule], []]:
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

    @overload
    def construct_morphism(self, domain: SetObject, codomain: SetObject, rule: Rule) -> SetMap: ...

    @overload
    def construct_morphism(self, domain: SetObject, codomain: SetObject, rule: Rule, inverse_rule: Rule) -> SetMap: ...

    def construct_morphism(self, domain: SetObject, codomain: SetObject, rule: Rule, *inverse_rule: Rule) -> SetMap:
        """``Mor(Sets())(X, Y)(rule)`` or, with an inverse rule, an isomorphism retaining its inverse."""
        assert domain in self and codomain in self
        morphisms = self.morphism_category(1)
        forward = self.MorphismType(morphisms, domain, codomain, rule)
        if not inverse_rule:
            return forward
        (backward_rule,) = inverse_rule
        self._retain_inverses(forward, self.MorphismType(morphisms, codomain, domain, backward_rule))
        return forward

    def _retain_inverses(self, forward: SetMap, backward: SetMap) -> None:
        """Record two maps as mutually inverse and place both in ``Isomorphisms()``."""
        self._inverses[forward] = backward
        self._inverses[backward] = forward
        isomorphisms = self.morphism_category(1).Isomorphisms()
        refine(forward, isomorphisms)
        refine(backward, isomorphisms)

    def construct_identity(self, member_object: SetObject) -> SetMap:
        identity = self.MorphismType(self.morphism_category(1), member_object, member_object, lambda datum: datum)
        self._retain_inverses(identity, identity)
        return identity

    def composite(self, second: SetMap, first: SetMap) -> SetMap:
        morphisms = self.morphism_category(1)
        assert first in morphisms and second in morphisms
        assert first.codomain() is second.domain(), f"{second!r} after {first!r} is not composable"
        composite = self.MorphismType(morphisms, first.domain(), second.codomain(), lambda datum: second._rule(first._rule(datum)))
        if first in self._inverses and second in self._inverses:
            first_inverse, second_inverse = self._inverses[first], self._inverses[second]
            inverse = self.MorphismType(morphisms, second.codomain(), first.domain(), lambda datum: first_inverse._rule(second_inverse._rule(datum)))
            self._retain_inverses(composite, inverse)
        return composite

    def inverse_morphism(self, morphism: SetMap) -> SetMap:
        """The inverse of an isomorphism (D09).

        The retained inverse when the construction supplied one; else the exact inverse
        of a bijection out of a finite enumerable set; else the owned symbolic inverse,
        whose equations hold by placement in ``Isomorphisms()`` and whose evaluation
        has no executable rule.
        """
        if morphism in self._inverses:
            return self._inverses[morphism]
        finite = self.Finite()
        domain, codomain = morphism.domain(), morphism.codomain()
        if finite.has_chosen_enumeration(domain):
            preimages = {morphism._rule(datum): datum for datum in finite.chosen_enumeration(domain)}
            self._retain_inverses(morphism, self.MorphismType(self.morphism_category(1), codomain, domain, lambda datum: preimages[datum]))
            return self._inverses[morphism]

        def no_rule(datum: Datum) -> Datum:
            assert False, f"the inverse of {morphism!r} has no executable rule; its equations hold by placement in Isomorphisms()"

        symbolic = self.MorphismType(self.morphism_category(1), codomain, domain, no_rule)
        self._retain_inverses(morphism, symbolic)
        refine(symbolic, self.morphism_category(1)(codomain, domain).Isomorphisms())
        return symbolic

    # -- owned constructions (D16; ``sets/products.py``, ``sets/exponentials.py``) ---

    def limit_construction(self, shape: Category) -> Callable[[Functor], SetObject]:
        """Products over ``Discrete(S)``; general limits by compatible families arrive with the limits unit."""
        from sage_categories.cat.shapes import is_discrete
        from sage_categories.sets.products import product_of_sets

        assert is_discrete(shape), (
            f"Sets owns no {shape!r}-limit construction in this unit: only products over Discrete(S); "
            "general limits as sets of compatible families belong to Unit B; supply universal data"
        )
        return product_of_sets

    def colimit_construction(self, shape: Category) -> Callable[[Functor], SetObject]:
        """Coproducts over ``Discrete(S)``; general colimits by quotients arrive with the limits unit."""
        from sage_categories.cat.shapes import is_discrete
        from sage_categories.sets.products import coproduct_of_sets

        assert is_discrete(shape), (
            f"Sets owns no {shape!r}-colimit construction in this unit: only coproducts over Discrete(S); "
            "general colimits as quotients of coproducts belong to Unit B; supply universal data"
        )
        return coproduct_of_sets

    def exponential(self, exponent: SetObject, base: SetObject) -> SetObject:
        """``base ** exponent``: the function set (POL-SET-017)."""
        from sage_categories.sets.exponentials import function_set

        assert exponent in self and base in self
        return function_set(exponent, base)

    def name_of(self, set_map: SetMap) -> SetPoint:
        """The point of ``Y ** X`` naming a map ``X -> Y``."""
        from sage_categories.sets.exponentials import name_of

        assert set_map in self.morphism_category(1)
        return name_of(set_map)

    def evaluation(self, exponent: SetObject, base: SetObject) -> SetMap:
        """The evaluation morphism ``(base ** exponent) * exponent -> base`` retained by the exponential."""
        from sage_categories.sets.exponentials import evaluation_morphism

        assert exponent in self and base in self
        return evaluation_morphism(exponent, base)

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
