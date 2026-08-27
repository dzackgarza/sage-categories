"""``Cardinal()``: exact cardinal numbers, their representatives, and their morphisms (POL-ASSUME-004, POL-SET-025, ``specs/cardinality.md``).

A cardinal is an exact value: a finite cardinal, ``aleph(n)``, a cardinal power,
or a finite formal supremum formed by exact cardinal arithmetic.  There is no
placeholder cardinal and no unknown cardinal; cardinals implement no ``Unknown``
handling.  Construction is cached by expression, so an equal expression returns
the same object.

``Cardinal()`` is a skeletal presentation of ``Sets()``: each cardinal ``kappa``
selects one representative set ``R_kappa`` (Mathlib's ``Quotient.out`` of a cardinal
is such an arbitrary representative; ``specs/cardinality.md``, "Cardinal model").
The representative of a finite cardinal ``n`` is ``[n - 1] = {0, ..., n - 1}``, of
cardinality ``n`` (Mathlib ``Cardinal.mk_fin``; inspected 2026-08-27), and of ``0``
the empty set; the representative of an infinite cardinal is a rule-defined set
whose data are unknown and whose cardinality is recorded as ``kappa``
(POL-SET-031).  ``Mor(Cardinal())(kappa, lambda)`` is the discrete category on the
functions ``R_kappa -> R_lambda``: a cardinal morphism retains that set map, and
composition, identities, and inverses are those of the maps.  The one selected
structural functor sends a cardinal to its representative and a cardinal
morphism to its map; it is fully faithful because the hom categories are, by
definition, the function sets (the inclusion of a skeleton, Mathlib
``CategoryTheory.fromSkeleton`` with ``fromSkeleton.isEquivalence``; inspected
2026-08-27).  A cardinal is not placed in ``Sets()``: the functor is explicit, not
an identity-on-value inclusion (``specs/functor.md``, "Inclusion functors").

Cardinal order is the existence of an injection between the representatives:
``kappa <= lambda`` is ``Mor(Cardinal()).Monomorphisms()(kappa, lambda).is_inhabited()``
(Mathlib ``Cardinal.le_def``; inspected 2026-08-27), and cardinal equality is the
existence of a bijection (``Cardinal.eq``).  The exact handler of that inhabitation
is the comparison algorithm below, and a function ``R_kappa -> R_lambda`` exists
exactly when ``kappa = 0`` or ``lambda != 0`` (``nonempty_fun``).

Arithmetic normalizes by the rules of ``specs/cardinality.md``, each an inspected
theorem of Mathlib ``SetTheory.Cardinal`` (inspected 2026-08-26):

- finite sums, products, and powers evaluate exactly;
- ``a + b = max(a, b)`` for ``aleph0 <= a`` and ``b <= a`` (``Cardinal.add_eq_max``),
  so an infinite cardinal plus a finite one is unchanged, and a finite sum of
  infinite cardinals is their supremum;
- ``a * b = max(a, b)`` for infinite ``a, b`` (``Cardinal.mul_eq_max``), a positive
  finite cardinal times an infinite one is that infinite cardinal;
- ``0 ** k = 0`` for ``k > 0``, ``k ** 0 = 1``, ``1 ** k = 1``;
- ``c ** n = c`` for infinite ``c`` and finite ``n >= 1`` (``Cardinal.power_nat_eq``);
- ``n ** c = 2 ** c`` for ``2 <= n`` finite and infinite ``c`` (``Cardinal.nat_power_eq``);
- ``(a ** b) ** c = a ** (b * c)``;
- ``a < b ** a`` for ``1 < b`` (``Cardinal.cantor'``), so a power with an infinite
  exponent and a base of at least two is uncountable.

``aleph(alpha)`` takes an ordinal index ``alpha in Ordinals()`` (Mathlib
``Cardinal.aleph``, ``SetTheory.Cardinal.Aleph``); a Python ``int`` is the
finite-ordinal convenience.  The index ordinal is retained by identity, so
``aleph(alpha).aleph_index() is alpha``, and ``initial_ordinal()`` is
``omega(alpha)`` by ``Cardinal.ord_aleph`` (inspected 2026-08-26).

The cardinality functor ``#: core(Sets()) -> Cardinal()`` (``specs/cardinality.md``,
"Integration with ``Sets()``") sends a set to its cardinality and a bijection
``f: X -> Y`` to the conjugate ``b_Y * f * b_X^-1`` by the selected bijections
``b_X: X -> R_#X``.  The bijection of a finite enumerated set is the position map
of its enumeration; of a representative, its identity; of any other set with an
exact cardinality, a bijection with no executable rule, which exists by
``Cardinal.eq``.  A set whose cardinality is ``Unknown`` has no cardinal object,
so the functor has no executable value at it.

``Sets()`` is constructed first.  This module then constructs the ``Cardinal()``
singleton and binds its semantic role names.  ``aleph0`` and ``continuum`` are
module attributes resolved on first access.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage.structure.coerce_dict import MonoDict

import sage_categories.sets.category as _sets
import sage_categories.sets.objects as _set_objects
import sage_categories.ordinals.category as _ordinals
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.construction import (
    MorphismConstructionInput,
    ObjectConstructionInput,
    retained_morphism_input,
    retained_object_input,
)
from sage_categories.kernel.decisions import Decision, Unknown, decision_not, decision_or
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, ask
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, role_of
from sage_categories.ordinals.category import OrdinalObject, Ordinals
from sage_categories.sets.maps import SetMorphismData
from sage_categories.sets.objects import SetObjectData

if TYPE_CHECKING:
    from sage_categories.sets.elements import Datum
    from sage_categories.sets.maps import SetMap
    from sage_categories.sets.objects import SetObject

__all__ = ["Cardinal", "CardinalityMorphism", "CardinalObject", "aleph0", "cardinality_functor", "continuum", "representative_bijection"]

# A private expression key: nested tuples of strings and integers only, so caches
# and hashes never compare owned values.
type Key = tuple[str | int | Key, ...]


@dataclass(frozen=True, eq=False, slots=True)
class CardinalObjectData:
    """The normalized expression state introduced by ``Cardinal()``."""

    key: Key
    terms: tuple[CardinalObject, ...]


@dataclass(frozen=True, eq=False, slots=True)
class CardinalMorphismData:
    """The set map state introduced by a morphism of ``Cardinal()``."""

    set_map: SetMap


class CardinalObjectDeclaration(ObjectOfCategory):
    """An exact cardinal, retained by its normalized expression."""

    def __init__(self, data: CardinalObjectData) -> None:
        self._key = data.key
        self._terms = data.terms
        super().__init__()

    def _kind_(self) -> str:
        return self._key[0]

    def _terms_(self) -> tuple[CardinalObject, ...]:
        return self._terms

    def _finite_value_(self) -> int:
        assert self._kind_() == "finite"
        return self._key[1]

    def aleph_index(self) -> OrdinalObject:
        """The ordinal index of an aleph, retained by identity at construction."""
        assert self._kind_() == "aleph"
        return Cardinal()._aleph_indices[self]

    def initial_ordinal(self) -> OrdinalObject:
        """``omega(alpha)`` for ``aleph(alpha)``: Mathlib ``Cardinal.ord_aleph`` (inspected 2026-08-26)."""
        return Ordinals().omega(self.aleph_index())

    def cardinality(self) -> CardinalObject:
        return self

    def is_finite(self) -> AppliedPredicate:
        return Cardinal().Finite().predicate()(self)

    def is_infinite(self) -> AppliedPredicate:
        return Cardinal().Infinite().predicate()(self)

    def is_countable(self) -> AppliedPredicate:
        return Cardinal().Countable().predicate()(self)

    def is_uncountable(self) -> AppliedPredicate:
        return Cardinal().Uncountable().predicate()(self)

    def __add__(self, other: CardinalObject | int) -> CardinalObject:
        return Cardinal().sum(self, Cardinal()(other))

    def __radd__(self, other: int) -> CardinalObject:
        return Cardinal().sum(Cardinal()(other), self)

    def __mul__(self, other: CardinalObject | int) -> CardinalObject:
        return Cardinal().product(self, Cardinal()(other))

    def __rmul__(self, other: int) -> CardinalObject:
        return Cardinal().product(Cardinal()(other), self)

    def __pow__(self, exponent: CardinalObject | int) -> CardinalObject:
        return Cardinal().power(self, Cardinal()(exponent))

    def __rpow__(self, base: int) -> CardinalObject:
        return Cardinal().power(Cardinal()(base), self)

    def __le__(self, other: CardinalObject | int) -> AppliedPredicate:
        """``kappa <= lambda``: an injection ``R_kappa -> R_lambda`` exists (Mathlib ``Cardinal.le_def``)."""
        cardinals = Cardinal()
        return cardinals.morphism_category(1).Monomorphisms()(self, cardinals(other)).is_inhabited()

    def __lt__(self, other: CardinalObject | int) -> AppliedPredicate:
        return less_than(self, Cardinal()(other))

    def __ge__(self, other: CardinalObject | int) -> AppliedPredicate:
        return Cardinal()(other) <= self

    def __gt__(self, other: CardinalObject | int) -> AppliedPredicate:
        return less_than(Cardinal()(other), self)

    def __hash__(self) -> int:
        return hash(self._key)

    def __repr__(self) -> str:
        match self._kind_():
            case "finite":
                return str(self._finite_value_())
            case "aleph":
                return f"ℵ_{self.aleph_index()}"
            case "power":
                base, exponent = self._terms
                return f"({base!r})^({exponent!r})"
        return "sup(" + ", ".join(map(repr, self._terms)) + ")"


class CardinalMorphismDeclaration(MorphismOfCategory):
    """A morphism ``kappa -> lambda`` of ``Cardinal()``: a function between the representatives, retained as a set map."""

    def __init__(self, data: CardinalMorphismData) -> None:
        self._set_map = data.set_map
        super().__init__()

    def __repr__(self) -> str:
        return f"CardinalityMorphism({self.domain()!r} -> {self.codomain()!r})"


# ``less_than(kappa, lambda)``: ``kappa <= lambda`` and not ``kappa == lambda``.
less_than = Predicate("cardinal_less_than", 2, True)


class CardinalCategory(Category[[MorphismOfCategory], []]):
    """The skeletal category of cardinal representatives; its morphisms are the functions between representatives."""

    DeclaredObjectType = CardinalObjectDeclaration
    DeclaredMorphismType = CardinalMorphismDeclaration

    class DeclaredElementType(ElementOfObject):
        """A generalized element of a cardinal; no local operation."""

    def __init__(self) -> None:
        self._cardinals: dict[Key, CardinalObject] = {}
        self._aleph_indices: MonoDict = MonoDict()
        self._representatives: MonoDict = MonoDict()
        self._functors: dict[str, Functor] = {}
        super().__init__()
        self._equality.register_handler(self._equal)
        less_than.register_handler(self._less_than)
        self._countable_cardinals = PropertySubcategory(self, "Countable", {}, ())
        self._infinite_cardinals = PropertySubcategory(self, "Infinite", {}, ())
        self._finite_cardinals = PropertySubcategory(self, "Finite", {}, (self._countable_cardinals,))
        self._uncountable_cardinals = PropertySubcategory(self, "Uncountable", {}, (self._infinite_cardinals,))
        self._finite_cardinals.predicate().register_handler(self._is_finite)
        self._infinite_cardinals.predicate().register_handler(lambda cardinal: decision_not(self._is_finite(cardinal)))
        self._countable_cardinals.predicate().register_handler(self._is_countable)
        self._uncountable_cardinals.predicate().register_handler(lambda cardinal: decision_not(self._is_countable(cardinal)))

    def Finite(self) -> Category:
        return self._finite_cardinals

    def Infinite(self) -> Category:
        return self._infinite_cardinals

    def Countable(self) -> Category:
        return self._countable_cardinals

    def Uncountable(self) -> Category:
        return self._uncountable_cardinals

    # -- the skeletal presentation of ``Sets()`` (POL-SET-025) --------------------------

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.representative_functor(),)

    def representative_functor(self) -> Functor:
        """The functor ``Cardinal() -> Sets()`` sending ``kappa`` to ``R_kappa`` and a cardinal morphism to its map, retained once.

        Fully faithful by the definition of the morphisms of ``Cardinal()``: the skeleton
        inclusion (Mathlib ``CategoryTheory.fromSkeleton``, an equivalence; inspected 2026-08-27).
        """
        if "representative" not in self._functors:
            representative = Fun(self, _sets.Sets()).FullyFaithful()(self.representative, lambda morphism: morphism._set_map)

            def object_input(
                source: ObjectConstructionInput[CardinalObject, CardinalObjectData],
            ) -> ObjectConstructionInput[SetObject, SetObjectData]:
                cardinal = source.canonical_image
                if cardinal not in self._representatives:
                    self._representatives[cardinal] = self._select_representative(cardinal, source.datum)
                return retained_object_input(self._representatives[cardinal])

            def morphism_input(
                source: MorphismConstructionInput[CardinalMorphismData],
            ) -> MorphismConstructionInput[SetMorphismData]:
                return retained_morphism_input(source.datum.set_map)

            representative.retain_object_constructor_conversion(object_input)
            representative.retain_morphism_constructor_conversion(morphism_input)
            self._functors["representative"] = representative
        return self._functors["representative"]

    def representative(self, cardinal: CardinalObject) -> SetObject:
        """The selected representative set ``R_kappa``, one per cardinal."""
        return self.representative_functor().on_object(cardinal)

    def _select_representative(self, cardinal: CardinalObject, data: CardinalObjectData) -> SetObject:
        sets = _sets.Sets()
        if data.key[0] == "finite":
            # #[n - 1] = #{0, ..., n - 1} = n: Mathlib ``Cardinal.mk_fin`` (inspected 2026-08-27).
            size = data.key[1]
            assert isinstance(size, int)
            if size == 0:
                return sets._canonical_finite_from_cardinality("empty", (), (), cardinal)
            return sets._canonical_finite_from_cardinality("simplex", (size - 1,), tuple(range(size)), cardinal)

        def no_datum(datum: Datum) -> Decision:
            return Unknown

        return sets.rule_valued(no_datum, cardinal)

    # -- construction, cached by expression ---------------------------------------

    def _retain(self, key: Key, terms: tuple[CardinalObject, ...]) -> CardinalObject:
        if key not in self._cardinals:
            self._cardinals[key] = self.ObjectType(category=self, data=CardinalObjectData(key=key, terms=terms))
        return self._cardinals[key]

    def __call__(self, value: CardinalObject | int) -> CardinalObject:
        """``Cardinal()(n)`` for a nonnegative integer; a cardinal is returned unchanged."""
        if value in self:
            return value
        assert value >= 0, f"{value!r} is not a cardinal"
        return self._retain(("finite", value), ())

    def aleph(self, index: OrdinalObject | int) -> CardinalObject:
        """``aleph(alpha)`` for an ordinal index; an ``int`` is the finite-ordinal convenience (Mathlib ``Cardinal.aleph``)."""
        ordinal_index = Ordinals()(index)
        key: Key = ("aleph", ordinal_index._expression_key_())
        if key not in self._cardinals:
            self._aleph_indices[self._retain(key, ())] = ordinal_index
        return self._cardinals[key]

    def zero(self) -> CardinalObject:
        return self(0)

    def one(self) -> CardinalObject:
        return self(1)

    def _finite(self, cardinal: CardinalObject) -> bool:
        return self._is_finite(cardinal) is True

    def supremum(self, *cardinals: CardinalObject) -> CardinalObject:
        """The finite formal supremum, with dominated terms removed."""
        terms: list[CardinalObject] = []
        for cardinal in cardinals:
            terms.extend(cardinal._terms_() if cardinal._kind_() == "supremum" else (cardinal,))
        assert terms
        maximal: list[CardinalObject] = []
        for candidate in sorted(terms, key=lambda term: repr(term._key)):
            if any(self._at_most(candidate, term) is True for term in maximal):
                continue
            maximal = [term for term in maximal if self._at_most(term, candidate) is not True]
            maximal.append(candidate)
        if len(maximal) == 1:
            return maximal[0]
        return self._retain(("supremum", tuple(term._key for term in maximal)), tuple(maximal))

    def sum(self, first: CardinalObject, second: CardinalObject) -> CardinalObject:
        if self._finite(first) and self._finite(second):
            return self(first._finite_value_() + second._finite_value_())
        # Cardinal.add_eq_max: an infinite summand absorbs a smaller one.
        if self._finite(first):
            return second
        if self._finite(second):
            return first
        return self.supremum(first, second)

    def product(self, first: CardinalObject, second: CardinalObject) -> CardinalObject:
        if self._finite(first) and self._finite(second):
            return self(first._finite_value_() * second._finite_value_())
        if self._finite(first) and first._finite_value_() == 0 or self._finite(second) and second._finite_value_() == 0:
            return self(0)
        # Cardinal.mul_eq_max: a positive finite factor is absorbed by an infinite one.
        if self._finite(first):
            return second
        if self._finite(second):
            return first
        return self.supremum(first, second)

    def power(self, base: CardinalObject, exponent: CardinalObject) -> CardinalObject:
        if self._finite(exponent) and exponent._finite_value_() == 0:
            return self(1)
        if self._finite(base) and base._finite_value_() in (0, 1):
            return base
        if self._finite(base) and self._finite(exponent):
            return self(base._finite_value_() ** exponent._finite_value_())
        if self._finite(exponent):
            # Cardinal.power_nat_eq: c ** n = c for infinite c and n >= 1.
            return base
        if base._kind_() == "power":
            # (a ** b) ** c = a ** (b * c).
            inner_base, inner_exponent = base._terms_()
            return self.power(inner_base, self.product(inner_exponent, exponent))
        if base._kind_() == "supremum":
            return self.supremum(*(self.power(term, exponent) for term in base._terms_()))
        if self._finite(base):
            # Cardinal.nat_power_eq: n ** c = 2 ** c for finite n >= 2 and infinite c.
            base = self(2)
        elif self._at_most(base, exponent) is True:
            # Cardinal.power_eq_two_power: a ** c = 2 ** c for 2 <= a <= c and infinite c
            # (inspected 2026-08-27); in particular c ** c = 2 ** c (Cardinal.power_self_eq).
            base = self(2)
        return self._retain(("power", base._key, exponent._key), (base, exponent))

    # -- morphisms: functions between the representatives (``specs/cardinality.md``, "Cardinal morphisms") --

    def construct_morphism(self, domain: CardinalObject, codomain: CardinalObject, set_map: SetMap) -> CardinalityMorphism:
        """``Mor(Cardinal())(kappa, lambda)(f)`` for a set map ``f: R_kappa -> R_lambda``."""
        assert domain in self and codomain in self
        assert set_map in _sets.Sets().morphism_category(1)(self.representative(domain), self.representative(codomain)), (
            f"{set_map!r} is not a map from the representative of {domain!r} to the representative of {codomain!r}"
        )
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=domain,
            codomain=codomain,
            data=CardinalMorphismData(set_map=set_map),
        )

    def construct_identity(self, cardinal: CardinalObject) -> CardinalityMorphism:
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=cardinal,
            codomain=cardinal,
            data=CardinalMorphismData(set_map=self.representative(cardinal).identity()),
        )

    def composite(self, second: CardinalityMorphism, first: CardinalityMorphism) -> CardinalityMorphism:
        """Composition is the composition of the maps between representatives."""
        morphisms = self.morphism_category(1)
        assert first in morphisms and second in morphisms
        assert first.codomain() is second.domain(), f"{second!r} after {first!r} is not composable"
        return self.MorphismType(
            category=morphisms,
            domain=first.domain(),
            codomain=second.codomain(),
            data=CardinalMorphismData(set_map=second._set_map * first._set_map),
        )

    def inverse_morphism(self, morphism: CardinalityMorphism) -> CardinalityMorphism:
        """The inverse of a cardinal isomorphism: the inverse of its map, an isomorphism of sets because the fully faithful representative functor reflects isomorphisms (Mathlib ``CategoryTheory.isIso_of_fully_faithful``; inspected 2026-08-27)."""
        if morphism not in self._inverses:
            set_map = _sets.Sets().morphism_category(1).Isomorphisms()(morphism._set_map)
            inverse = self.MorphismType(
                category=self.morphism_category(1),
                domain=morphism.codomain(),
                codomain=morphism.domain(),
                data=CardinalMorphismData(set_map=set_map.inverse()),
            )
            self.retain_inverses(morphism, inverse)
        return self._inverses[morphism]

    def hom_inhabited(self, hom_category: Category) -> Decision:
        """Inhabitation of ``Mor(Cardinal())(kappa, lambda)`` and of its monomorphism and isomorphism narrowings.

        A function ``R_kappa -> R_lambda`` exists exactly when ``kappa = 0`` or
        ``lambda != 0`` (Mathlib ``nonempty_fun``); an injection exactly when
        ``kappa <= lambda`` (``Cardinal.le_def``), decided by the comparison
        algorithm; a bijection exactly when ``kappa = lambda`` (``Cardinal.eq``).
        All inspected 2026-08-27.
        """
        base = hom_category.narrowing_base()
        source, target = base.domain(), base.codomain()
        morphisms = self.morphism_category(1)
        match hom_category.narrowing_roots():
            case ():
                return decision_or(self._equal(source, self(0)), decision_not(self._equal(target, self(0))))
            case (root,) if root is morphisms.Monomorphisms():
                return self._at_most(source, target)
            case (root,) if root is morphisms.Isomorphisms():
                return self._equal(source, target)
        return Unknown

    # -- exact decisions -----------------------------------------------------------

    def _is_finite(self, cardinal: CardinalObject) -> Decision:
        match cardinal._kind_():
            case "finite":
                return True
            case "aleph" | "power":
                return False
        return all(self._is_finite(term) is True for term in cardinal._terms_())

    def _is_countable(self, cardinal: CardinalObject) -> Decision:
        match cardinal._kind_():
            case "finite":
                return True
            case "aleph":
                # Cardinal.aleph0_lt_aleph: aleph(o) is uncountable exactly when 0 < o.
                return ask(cardinal.aleph_index() == 0)
            case "power":
                # Cardinal.cantor': a < b ** a for 1 < b, so 2 ** (infinite) exceeds aleph0.
                return False
        return all(self._is_countable(term) is True for term in cardinal._terms_())

    def _equal(self, first: CategoryPoint, candidate: Any) -> Decision:
        if first not in self:
            return Unknown
        if candidate in self:
            second = candidate
        elif role_of(candidate) is None:
            second = self(candidate)
        else:
            return Unknown
        if first._key == second._key:
            return True
        if self._at_most(first, second) is False or self._at_most(second, first) is False:
            return False
        return Unknown

    def _at_most(self, first: CardinalObject, second: CardinalObject) -> Decision:
        if first._key == second._key:
            return True
        if first._kind_() == "supremum":
            answers = [self._at_most(term, second) for term in first._terms_()]
            if all(answer is True for answer in answers):
                return True
            if any(answer is False for answer in answers):
                return False
            return Unknown
        if second._kind_() == "supremum":
            if any(self._at_most(first, term) is True for term in second._terms_()):
                return True
            return Unknown
        if self._finite(first) and self._finite(second):
            return first._finite_value_() <= second._finite_value_()
        if self._finite(first):
            return True
        if self._finite(second):
            return False
        if first._kind_() == "aleph" and second._kind_() == "aleph":
            # Cardinal.aleph_le_aleph: alephs are ordered by their ordinal indices.
            return ask(first.aleph_index() <= second.aleph_index())
        if first._kind_() == "aleph" and ask(first.aleph_index() == 0) is True:
            return True
        if first._kind_() == "aleph" and ask(first.aleph_index() == 1) is True and self._is_countable(second) is False:
            return True
        if first._kind_() == "power":
            base, exponent = first._terms_()
            # Cardinal.cantor': b ** a > a for 1 < b, so b ** a is not below anything below a.
            if self._at_most(self(2), base) is True and self._at_most(second, exponent) is True:
                return False
        if second._kind_() == "power":
            base, exponent = second._terms_()
            if self._at_most(first, base) is True:
                return True
            # Cardinal.cantor': the exponent is below a power with base at least two.
            if self._at_most(self(2), base) is True and self._at_most(first, exponent) is True:
                return True
            if first._kind_() == "power":
                first_base, first_exponent = first._terms_()
                if self._at_most(first_base, base) is True and self._at_most(first_exponent, exponent) is True:
                    return True
        return Unknown

    def _less_than(self, first: CardinalObject, second: CardinalObject) -> Decision:
        if first._key == second._key:
            return False
        if self._at_most(first, second) is True:
            return decision_not(ask(first == second))
        if self._at_most(second, first) is True:
            return False
        return Unknown

    def __repr__(self) -> str:
        return "Cardinal"


_CARDINAL = CardinalCategory()
CardinalObject = _CARDINAL.ObjectType
CardinalityMorphism = _CARDINAL.MorphismType
_sets.CardinalObject = CardinalObject
_set_objects.CardinalObject = CardinalObject
_ordinals.CardinalObject = CardinalObject


def Cardinal() -> CardinalCategory:
    """The category of exact cardinals."""
    return _CARDINAL


def __getattr__(name: str) -> CardinalObject:
    """``aleph0`` and ``continuum`` are constructed with ``Cardinal()``, on first access."""
    match name:
        case "aleph0":
            return Cardinal().aleph(0)
        case "continuum":
            return Cardinal()(2) ** Cardinal().aleph(0)
    raise AttributeError(name)


if TYPE_CHECKING:
    aleph0: CardinalObject
    continuum: CardinalObject


# -- the cardinality functor ``#: core(Sets()) -> Cardinal()`` -------------------------------------

_representative_bijections: MonoDict = MonoDict()


def representative_bijection(member_object: SetObject) -> SetMap:
    """The selected bijection ``X -> R_#X``, retained per set; ``X`` needs an exact cardinality."""
    sets, cardinals = _sets.Sets(), Cardinal()
    if member_object not in _representative_bijections:
        cardinality = member_object.cardinality()
        assert cardinality is not Unknown, f"{member_object!r} has no known cardinality, so no bijection with a representative is selected"
        representative = cardinals.representative(cardinality)
        finite = sets.Finite()
        if representative is member_object:
            _representative_bijections[member_object] = member_object.identity()
        elif finite.has_chosen_enumeration(member_object):
            # The position map of the chosen enumeration onto ``{0, ..., n - 1}``.
            enumeration = finite.chosen_enumeration(member_object)
            positions = {datum: position for position, datum in enumerate(enumeration)}
            _representative_bijections[member_object] = sets.construct_morphism(member_object, representative, positions.__getitem__, enumeration.__getitem__)
        else:

            def no_rule(datum: Datum) -> Datum:
                assert False, f"the selected bijection between {member_object!r} and {representative!r} has no executable rule; it exists by the definition of cardinality"

            _representative_bijections[member_object] = sets.construct_morphism(member_object, representative, no_rule, no_rule)
    return _representative_bijections[member_object]


def cardinality_functor() -> Functor:
    """``Sets().CardinalityFunctor()``: the object map ``X.cardinality()``, the morphism map the conjugate of a bijection by the selected bijections."""
    sets, cardinals = _sets.Sets(), Cardinal()

    def on_object(member_object: SetObject) -> CardinalObject:
        cardinality = member_object.cardinality()
        assert cardinality is not Unknown, f"{member_object!r} has no known cardinality, so the cardinality functor has no executable value at it"
        return cardinality

    def on_morphism(bijection: SetMap) -> CardinalityMorphism:
        source, target = bijection.domain(), bijection.codomain()
        conjugate = representative_bijection(target) * bijection * representative_bijection(source).inverse()
        return cardinals.morphism_category(1)(on_object(source), on_object(target)).Isomorphisms()(conjugate)

    return Fun(sets.Core(), cardinals)(on_object, on_morphism)
