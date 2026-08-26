"""``Sets()``: the category of sets and total maps (POL-SET-002, POL-CAT-083, POL-SET-013, POL-SET-026).

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
at ``Sets()`` (``inverse_morphism``); the inclusion of a chosen subset at
``Sets().ChosenSubsets()`` (``sets/subobjects.py``).
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
from sage_categories.kernel.decisions import UnknownClass
from sage_categories.sets.cardinals import Cardinal, CardinalObject
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
    from sage_categories.sets.subobjects import ChosenSubsetsCategory

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
        # An enumeration lists each member once: its length is the cardinality (POL-SET-011/027).
        for position, first in enumerate(enumeration):
            for second in enumeration[position + 1 :]:
                assert (first == second) is False, f"the enumeration lists {first!r} and {second!r}, which are not exactly distinct"
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
        self._constructions: dict[str, Category] = {}
        self._rule_valued: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(points_equal)
        self._equality.register_handler(maps_equal)
        countable = PropertySubcategory(self, "Countable", {}, ())
        infinite = PropertySubcategory(self, "Infinite", {}, ())
        finite = FiniteSets(self, "Finite", {Role.OBJECT: FiniteSetRole}, (countable,))
        uncountable = PropertySubcategory(self, "Uncountable", {}, (infinite,))
        # A known cardinality decides finiteness and countability (``specs/cardinality.md``); established
        # placement in the complementary property decides the negation (``specs/sets.md``, "Cardinality and enumeration").
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

    def rule_valued(self, membership_rule: MembershipRule, cardinality: CardinalObject | UnknownClass) -> SetObject:
        """A set whose data are rules (families, names of maps): its points are retained per datum object.

        The constructions that create such data (products over an unenumerated
        index, function sets, colimit representatives) construct their apex here, so
        ``X.point(datum)`` on it is ``X.rule_point(datum)``.
        """
        rule_valued = self.ObjectType(self, membership_rule, cardinality)
        self._rule_valued[rule_valued] = rule_valued
        return rule_valued

    def points_by_rule(self, member_object: SetObject) -> bool:
        """Whether ``member_object`` was constructed through ``rule_valued``."""
        return member_object in self._rule_valued

    def Finite(self) -> FiniteSets:
        return self._properties["Finite"]

    def Infinite(self) -> Category[[Rule], []]:
        return self._properties["Infinite"]

    def Countable(self) -> Category[[Rule], []]:
        return self._properties["Countable"]

    def Uncountable(self) -> Category[[Rule], []]:
        return self._properties["Uncountable"]

    def ChosenSubsets(self) -> ChosenSubsetsCategory:
        """The full subcategory of chosen subsets, each retaining its inclusion (``sets/subobjects.py``)."""
        from sage_categories.sets.subobjects import ChosenSubsetsCategory

        if "ChosenSubsets" not in self._constructions:
            self._constructions["ChosenSubsets"] = ChosenSubsetsCategory()
        return self._constructions["ChosenSubsets"]

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
        self.retain_inverses(forward, self.MorphismType(morphisms, codomain, domain, backward_rule))
        return forward

    def construct_identity(self, member_object: SetObject) -> SetMap:
        return self.MorphismType(self.morphism_category(1), member_object, member_object, lambda datum: datum)

    def composite(self, second: SetMap, first: SetMap) -> SetMap:
        morphisms = self.morphism_category(1)
        assert first in morphisms and second in morphisms
        assert first.codomain() is second.domain(), f"{second!r} after {first!r} is not composable"
        return self.MorphismType(morphisms, first.domain(), second.codomain(), lambda datum: second._rule(first._rule(datum)))

    def inverse_morphism(self, morphism: SetMap) -> SetMap:
        """The inverse of an isomorphism: the generic retained inverse, else the exact inverse of a
        bijection out of a finite enumerable set (POL-MATH-042), else the symbolic inverse."""
        finite = self.Finite()
        domain, codomain = morphism.domain(), morphism.codomain()
        if morphism not in self._inverses and finite.has_chosen_enumeration(domain):
            preimages = {morphism._rule(datum): datum for datum in finite.chosen_enumeration(domain)}
            self.retain_inverses(morphism, self.MorphismType(self.morphism_category(1), codomain, domain, lambda datum: preimages[datum]))
        return super().inverse_morphism(morphism)

    def _symbolic_inverse_(self, morphism: SetMap) -> SetMap:
        def no_rule(datum: Datum) -> Datum:
            assert False, f"the inverse of {morphism!r} has no executable rule; its equations hold by placement in Isomorphisms()"

        return self.morphism_category(1)(morphism.codomain(), morphism.domain()).Isomorphisms()(no_rule)

    # -- owned constructions (POL-SET-013; ``sets/products.py``, ``sets/exponentials.py``) ---

    def limit_construction(self, shape: Category) -> Callable[[Functor], SetObject]:
        """Products over ``Discrete(S)``; ``Sets()`` owns no other limit construction yet."""
        from sage_categories.cat.shapes import is_discrete
        from sage_categories.sets.products import product_of_sets

        assert is_discrete(shape), (
            f"Sets owns no {shape!r}-limit construction: only products over Discrete(S); "
            "the limit as the set of compatible families is not yet owned; supply universal data"
        )
        return product_of_sets

    def colimit_construction(self, shape: Category) -> Callable[[Functor], SetObject]:
        """Coproducts over ``Discrete(S)``; ``Sets()`` owns no other colimit construction yet."""
        from sage_categories.cat.shapes import is_discrete
        from sage_categories.sets.products import coproduct_of_sets

        assert is_discrete(shape), (
            f"Sets owns no {shape!r}-colimit construction: only coproducts over Discrete(S); "
            "the colimit as a quotient of the coproduct is not yet owned; supply universal data"
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

    def transpose(self, set_map: SetMap) -> SetMap:
        """The transpose ``Z -> Y ** X`` of a map ``Z * X -> Y`` out of a chosen binary product, retained per map."""
        from sage_categories.sets.exponentials import transpose

        assert set_map in self.morphism_category(1)
        return transpose(set_map)

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
