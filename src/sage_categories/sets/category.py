"""``Sets()``: the category of sets and total maps (POL-SET-002, POL-CAT-083, POL-SET-013, POL-SET-026).

``Sets()`` owns arbitrary sets and arbitrary functions.  Its objects are
rule-defined (``sets/objects.py``), its elements are maps ``T -> X`` with classical
points at the stage ``Sets().Terminal()`` (``sets/elements.py``), and its morphisms
are total maps by rule (``sets/maps.py``).  The property subcategories ``Finite()``,
``Infinite()``, ``Countable()``, and ``Uncountable()`` own the constructors that
supply their cardinal data; ``Finite => Countable`` and ``Uncountable => Infinite``
are their recorded subcategory monomorphisms.  The canonical objects ``Empty()``, ``Terminal()``,
and ``Simplex(n)`` exist once by identity.

Retained construction data, each keyed by identity at its owner: the chosen
enumeration of a finite set at ``Sets().Finite()``; the inverse of an isomorphism
at ``Sets()`` (``inverse_morphism``); the presenting monomorphism of a chosen subset at
``Sets().ChosenSubsets()`` (``sets/subobjects.py``).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, overload

from sage.misc.cachefunc import cached_method
from sage.structure.coerce_dict import MonoDict

from sage_categories.sets import elements as _set_elements
from sage_categories.sets import maps as _set_maps
from sage_categories.sets import objects as _set_objects
from sage_categories.cat.category import Category
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.decisions import Decision, Unknown, decision_not, decision_or
from sage_categories.kernel.predicates import ask
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import Role
from sage_categories.kernel.decisions import UnknownClass
from sage_categories.sets.elements import Datum, SetElementData, SetElementDeclaration, SetPointData, points_equal
from sage_categories.sets.maps import (
    Rule,
    SetMorphismData,
    SetMapDeclaration,
    bijective_on_finite_domain,
    injective_on_finite_domain,
    maps_equal,
    surjective_on_finite_domain,
)
from sage_categories.sets.objects import FiniteSetRole, MembershipRule, SetObjectData, SetObjectDeclaration, sets_equal

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor
    from sage_categories.sets.cardinals import CardinalObject
    from sage_categories.sets.finite_subsets import FiniteSubsetsCategory, FinitelySupportedFunctionsCategory, SizedSubsetsCategory
    from sage_categories.sets.power_objects import PowerObjectsCategory
    from sage_categories.sets.subobjects import ChosenQuotientsCategory, ChosenSubsetsCategory

__all__ = ["SetElement", "SetMap", "SetObject", "Sets", "SetsCategory"]


class FiniteSets(PropertySubcategory[[Rule], []]):
    """``Sets().Finite()``: owns construction from an explicit finite enumeration and retains it."""

    def __init__(self, ambient: Category[[Rule], []], name: str, roles: dict[Role, type], implications: tuple[Category, ...]) -> None:
        self._enumerations: MonoDict = MonoDict()
        super().__init__(ambient, name, roles, implications)

    def __call__(self, members: SetObject | Iterable[Datum]) -> SetObject:
        """Refine a set of ``Sets()``, or construct the finite set with the given enumeration."""
        from sage_categories.sets.cardinals import Cardinal

        if members in self.ambient():
            refine(members, self)
            return members
        enumeration = tuple(members)
        return self._from_enumeration(enumeration, Cardinal()(len(enumeration)))

    def _from_enumeration(self, enumeration: tuple[Datum, ...], cardinality: CardinalObject) -> SetObject:
        """Construct the finite set with this exact enumeration and cardinal."""
        # An enumeration lists each member once: its length is the cardinality (POL-SET-011/027).
        for position, first in enumerate(enumeration):
            for second in enumeration[position + 1 :]:
                assert (first == second) is False, f"the enumeration lists {first!r} and {second!r}, which are not exactly distinct"
        ambient = self.ambient()
        finite_set = ambient.ObjectType(
            ambient,
            SetObjectData(
                lambda datum: any(datum == member for member in enumeration),
                cardinality,
            ),
        )
        refine(finite_set, self)
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

    DeclaredObjectType = SetObjectDeclaration
    DeclaredElementType = SetElementDeclaration
    DeclaredMorphismType = SetMapDeclaration

    def __init__(self) -> None:
        self._canonical: dict[tuple[str, tuple[int, ...]], SetObject] = {}
        self._rule_valued: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(points_equal)
        self._equality.register_handler(sets_equal)
        self._equality.register_handler(maps_equal)
        self._countable = PropertySubcategory(self, "Countable", {}, ())
        self._infinite = PropertySubcategory(self, "Infinite", {}, ())
        self._finite = FiniteSets(self, "Finite", {Role.OBJECT: FiniteSetRole}, (self._countable,))
        self._uncountable = PropertySubcategory(self, "Uncountable", {}, (self._infinite,))
        # A known cardinality decides finiteness and countability (``specs/cardinality.md``); established
        # placement in the complementary property decides the negation (``specs/sets.md``, "Cardinality and enumeration").
        self._finite.predicate().register_handler(self._finite_by_cardinality)
        self._finite.predicate().register_handler(lambda ambient: False if ambient in self._infinite else Unknown)
        self._countable.predicate().register_handler(self._countable_by_cardinality)
        self._countable.predicate().register_handler(lambda ambient: False if ambient in self._uncountable else Unknown)
        self._infinite.predicate().register_handler(lambda ambient: decision_not(ask(ambient.is_finite())))
        self._uncountable.predicate().register_handler(lambda ambient: decision_not(ask(ambient.is_countable())))
        morphisms = self.morphism_category(1)
        morphisms.Monomorphisms().predicate().register_handler(injective_on_finite_domain)
        morphisms.Epimorphisms().predicate().register_handler(surjective_on_finite_domain)
        morphisms.Isomorphisms().predicate().register_handler(bijective_on_finite_domain)

    # -- construction ----------------------------------------------------------------

    def __call__(self, membership_rule: MembershipRule) -> SetObject:
        """``Sets()(rule)``: the set defined by a membership rule on data, with no cardinal data."""
        return self.ObjectType(self, SetObjectData(membership_rule, Unknown))

    def with_cardinality(self, membership_rule: MembershipRule, cardinality: CardinalObject) -> SetObject:
        """The set defined by a membership rule whose exact cardinality a construction theorem supplies (POL-SET-031, POL-MATH-024)."""
        from sage_categories.sets.cardinals import Cardinal

        assert cardinality in Cardinal(), f"{cardinality!r} is not a cardinal"
        return self.ObjectType(self, SetObjectData(membership_rule, cardinality))

    def rule_valued(self, membership_rule: MembershipRule, cardinality: CardinalObject | UnknownClass) -> SetObject:
        """A set whose data are rules (families, names of maps): its points are retained per datum object.

        The constructions that create such data (products over an unenumerated
        index, function sets, colimit representatives) construct their apex here, so
        ``X.point(datum)`` on it is ``X.rule_point(datum)``.
        """
        rule_valued = self.ObjectType(self, SetObjectData(membership_rule, cardinality))
        self._rule_valued[rule_valued] = rule_valued
        return rule_valued

    def points_by_rule(self, member_object: SetObject) -> bool:
        """Whether ``member_object`` was constructed through ``rule_valued``."""
        return member_object in self._rule_valued

    def Finite(self) -> FiniteSets:
        return self._finite

    def Infinite(self) -> Category[[Rule], []]:
        return self._infinite

    def Countable(self) -> Category[[Rule], []]:
        return self._countable

    def Uncountable(self) -> Category[[Rule], []]:
        return self._uncountable

    @cached_method
    def ChosenSubsets(self) -> ChosenSubsetsCategory:
        """The construction family of chosen subsets, each retaining its monomorphism (``sets/subobjects.py``)."""
        from sage_categories.sets.subobjects import ChosenSubsetsCategory

        return ChosenSubsetsCategory(self)

    @cached_method
    def ChosenQuotients(self) -> ChosenQuotientsCategory:
        """The construction family of chosen quotients, each retaining its quotient map (``sets/subobjects.py``)."""
        from sage_categories.sets.subobjects import ChosenQuotientsCategory

        return ChosenQuotientsCategory(self)

    def _canonical_finite(self, name: str, arguments: tuple[int, ...], members: Iterable[Datum]) -> SetObject:
        if (name, arguments) not in self._canonical:
            self._canonical[name, arguments] = self.Finite()(members)
        return self._canonical[name, arguments]

    def _canonical_finite_from_cardinality(
        self,
        name: str,
        arguments: tuple[int, ...],
        members: tuple[Datum, ...],
        cardinality: CardinalObject,
    ) -> SetObject:
        """Retain a canonical finite set whose construction already supplies its cardinal."""
        if (name, arguments) not in self._canonical:
            self._canonical[name, arguments] = self.Finite()._from_enumeration(members, cardinality)
        return self._canonical[name, arguments]

    def Empty(self) -> SetObject:
        """The empty set: the representative that ``Cardinal()`` selects for ``0`` (``sets/cardinals.py``)."""
        from sage_categories.sets.cardinals import Cardinal

        return Cardinal().representative(Cardinal().zero())

    def Terminal(self) -> SetObject:
        """The one-point set ``1 = {*}``, the classical stage of ``Sets()``."""
        return self._canonical_finite("terminal", (), ((),))

    def Simplex(self, dimension: int) -> SetObject:
        """``[n] = {0, ..., n}``: the representative that ``Cardinal()`` selects for ``n + 1`` (Mathlib ``Cardinal.mk_fin``; ``sets/cardinals.py``)."""
        from sage_categories.sets.cardinals import Cardinal

        assert dimension >= 0
        return Cardinal().representative(Cardinal()(dimension + 1))

    def separating_family(self) -> tuple[SetObject, ...]:
        """``G_Sets = 1``.  The writer asserts that ``1`` separates ``Sets()``, so ``Mor(Sets())(1, -)`` is faithful (POL-MATH-037).

        nLab "separator", Definitions ("if ``f . e = g . e`` for every morphism
        ``e: S -> X``, then ``f = g``") and Examples and applications ("In Set, any
        inhabited set is a separator; in particular, the point is a separator");
        inspected 2026-08-27.  Set membership, enumeration, and cardinality read
        ``Mor(Sets())(1, X)`` through this stage.
        """
        return (self.Terminal(),)

    @cached_method
    def CardinalityFunctor(self) -> Functor:
        """``#: core(Sets()) -> Cardinal()``, retained once (``specs/cardinality.md``, "Integration with ``Sets()``"; ``sets/cardinals.py``)."""
        from sage_categories.sets.cardinals import cardinality_functor

        return cardinality_functor()

    def element_from_defining_morphism(self, defining_morphism: SetMap) -> SetElement:
        """The generalized element defined by ``T -> X``, retained by that exact map (POL-CAT-066)."""
        assert defining_morphism in self.morphism_category(1), f"{defining_morphism!r} is not a set morphism"
        if defining_morphism not in self._elements:
            if defining_morphism.domain() is self.Terminal():
                state = SetPointData(defining_morphism._set_morphism_data.rule(()))
            else:
                state = SetElementData()
            self._elements[defining_morphism] = defining_morphism.codomain().category().ElementType(defining_morphism, state)
        return self._elements[defining_morphism]

    # -- morphisms ----------------------------------------------------------------------

    @overload
    def construct_morphism(self, domain: SetObject, codomain: SetObject, rule: Rule) -> SetMap: ...

    @overload
    def construct_morphism(self, domain: SetObject, codomain: SetObject, rule: Rule, inverse_rule: Rule) -> SetMap: ...

    def construct_morphism(self, domain: SetObject, codomain: SetObject, rule: Rule, *inverse_rule: Rule) -> SetMap:
        """``Mor(Sets())(X, Y)(rule)`` or, with an inverse rule, an isomorphism retaining its inverse."""
        assert domain in self and codomain in self
        morphisms = self.morphism_category(1)
        forward = self.MorphismType(morphisms, domain, codomain, SetMorphismData(rule))
        if not inverse_rule:
            return forward
        (backward_rule,) = inverse_rule
        self.retain_inverses(
            forward,
            self.MorphismType(morphisms, codomain, domain, SetMorphismData(backward_rule)),
        )
        return forward

    def construct_identity(self, member_object: SetObject) -> SetMap:
        return self.MorphismType(
            self.morphism_category(1),
            member_object,
            member_object,
            SetMorphismData(lambda datum: datum),
        )

    def composite(self, second: SetMap, first: SetMap) -> SetMap:
        morphisms = self.morphism_category(1)
        assert first in morphisms and second in morphisms
        assert first.codomain() is second.domain(), f"{second!r} after {first!r} is not composable"
        first_rule = first._set_morphism_data.rule
        second_rule = second._set_morphism_data.rule
        return self.MorphismType(
            morphisms,
            first.domain(),
            second.codomain(),
            SetMorphismData(lambda datum: second_rule(first_rule(datum))),
        )

    def inverse_morphism(self, morphism: SetMap) -> SetMap:
        """The inverse of an isomorphism: the generic retained inverse, else the exact inverse of a
        bijection out of a finite enumerable set (POL-MATH-042), else the symbolic inverse."""
        finite = self.Finite()
        domain, codomain = morphism.domain(), morphism.codomain()
        if morphism not in self._inverses and finite.has_chosen_enumeration(domain):
            rule = morphism._set_morphism_data.rule
            preimages = {rule(datum): datum for datum in finite.chosen_enumeration(domain)}
            self.retain_inverses(
                morphism,
                self.MorphismType(
                    self.morphism_category(1),
                    codomain,
                    domain,
                    SetMorphismData(lambda datum: preimages[datum]),
                ),
            )
        return super().inverse_morphism(morphism)

    def _symbolic_inverse_(self, morphism: SetMap) -> SetMap:
        def no_rule(datum: Datum) -> Datum:
            assert False, f"the inverse of {morphism!r} has no executable rule; its equations hold by placement in Isomorphisms()"

        return self.morphism_category(1)(morphism.codomain(), morphism.domain()).Isomorphisms()(no_rule)

    # -- owned constructions (POL-SET-013; ``sets/products.py``, ``sets/exponentials.py``) ---

    def limit_construction(self, shape: Category) -> Callable[[Functor], SetObject]:
        """Products over ``Discrete(S)``; over every other shape, the compatible families (``sets/limits.py``)."""
        from sage_categories.cat.shapes import is_discrete
        from sage_categories.sets.limits import limit_of_sets
        from sage_categories.sets.products import product_of_sets

        if is_discrete(shape):
            return product_of_sets
        return limit_of_sets

    def colimit_construction(self, shape: Category) -> Callable[[Functor], SetObject]:
        """Coproducts over ``Discrete(S)``; over every other shape, the quotient of the coproduct (``sets/limits.py``)."""
        from sage_categories.cat.shapes import is_discrete
        from sage_categories.sets.limits import colimit_of_sets
        from sage_categories.sets.products import coproduct_of_sets

        if is_discrete(shape):
            return coproduct_of_sets
        return colimit_of_sets

    def exponential(self, exponent: SetObject, base: SetObject) -> SetObject:
        """``base ** exponent``: the function set (POL-SET-017); for ``base = [1]`` the power object ``2 ** exponent`` (POL-SET-018)."""
        from sage_categories.sets.exponentials import function_set

        assert exponent in self and base in self
        if base is self.Simplex(1):
            return self.PowerObjects()(exponent)
        return function_set(exponent, base)

    @cached_method
    def PowerObjects(self) -> PowerObjectsCategory:
        """The narrowing of power objects ``2 ** X``, each retaining its base set (``sets/power_objects.py``)."""
        from sage_categories.sets.power_objects import PowerObjectsCategory

        return PowerObjectsCategory(self)

    @cached_method
    def FiniteSubsets(self) -> FiniteSubsetsCategory:
        """The narrowing of the sets of finite subsets ``FiniteSubsets()(X)`` (``sets/finite_subsets.py``)."""
        from sage_categories.sets.finite_subsets import FiniteSubsetsCategory

        return FiniteSubsetsCategory(self)

    @cached_method
    def SubsetsOfSize(self, size: int) -> SizedSubsetsCategory:
        """``Sets().SubsetsOfSize(k)``, one narrowing per ``k``, whose constructor ``(X)`` is the set of subsets of ``X`` of size ``k``."""
        from sage_categories.sets.finite_subsets import SizedSubsetsCategory

        return SizedSubsetsCategory(self, size)

    @cached_method
    def FinitelySupportedFunctions(self) -> FinitelySupportedFunctionsCategory:
        """The narrowing of the finitely supported function sets ``X^(S)`` (``sets/finite_subsets.py``)."""
        from sage_categories.sets.finite_subsets import FinitelySupportedFunctionsCategory

        return FinitelySupportedFunctionsCategory(self)

    def name_of(self, set_map: SetMap) -> SetElement:
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

    def hom_inhabited(self, hom_category: Category) -> Decision:
        """Inhabitation of ``Mor(Sets())(A, B)`` and of its isomorphism and monomorphism narrowings, from the cardinalities.

        Each case is a Mathlib theorem (inspected 2026-08-27): a function ``A -> B``
        exists exactly when ``A`` is empty or ``B`` is nonempty (``nonempty_fun``); a
        bijection exists exactly when ``#A = #B`` (``Cardinal.eq``); an injection
        exactly when ``#A <= #B`` (``Cardinal.le_def``).  ``Unknown`` when a needed
        cardinality is unknown or the narrowing is another one.
        """
        base = hom_category.narrowing_base()
        source, target = base.domain().cardinality(), base.codomain().cardinality()
        morphisms = self.morphism_category(1)
        match hom_category.narrowing_roots():
            case ():
                source_empty = Unknown if source is Unknown else ask(source == 0)
                target_empty = Unknown if target is Unknown else ask(target == 0)
                return decision_or(source_empty, decision_not(target_empty))
        if source is Unknown or target is Unknown:
            return Unknown
        match hom_category.narrowing_roots():
            case (root,) if root is morphisms.Isomorphisms():
                return ask(source == target)
            case (root,) if root is morphisms.Monomorphisms():
                return ask(source <= target)
        return Unknown

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
SetObject = _SETS.ObjectType
SetElement = _SETS.ElementType
SetMap = _SETS.MorphismType

_set_objects.SetObject = SetObject
_set_objects.SetElement = SetElement
_set_elements.SetElement = SetElement
_set_maps.SetObject = SetObject
_set_maps.SetElement = SetElement


def Sets() -> SetsCategory:
    """The category of sets."""
    return _SETS
