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
definition, the function sets (the monomorphism of a skeleton, Mathlib
``CategoryTheory.fromSkeleton`` with ``fromSkeleton.isEquivalence``; inspected
2026-08-27).  A cardinal is not placed in ``Sets()``: the functor is explicit, not
an identity-on-values monomorphism (``specs/functor.md``, "Monomorphisms of ``Cat()`` and placement").

Cardinal order is the inhabitation of ``Mor(Cardinal()).Monomorphisms()(kappa, lambda)``,
which is the existence of an injection ``R_kappa -> R_lambda`` (Mathlib
``Cardinal.le_def``; inspected 2026-08-27); cardinal equality is the existence of a
bijection (``Cardinal.eq``), and a function ``R_kappa -> R_lambda`` exists exactly when
``kappa = 0`` or ``lambda != 0`` (``nonempty_fun``).  That states what the order *is*.
What decides it is ``CardinalSemiring.le``: the algebra of the normalized expressions,
one rule per theorem, constructing no representative and no injection.  Nothing else
could decide it, because the representative of an infinite cardinal has no enumerable
data from which to build a map.  ``Cardinal.le_def`` is the theorem that makes an answer
about the expressions an answer about injections, and each rule below cites the theorem
that licenses it.  A pair no rule decides is ``Unknown``, not false.

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

Those are the rules ZFC alone supplies.  The generalized continuum hypothesis is an
assumable proposition here, and this module records it at load, so the package's default
state assumes it (``specs/cardinality.md``, "The continuum hypothesis").  Assumed, it
decides every infinite power, so ``2 ** aleph(0)`` is ``aleph(1)`` and the normal form of
an infinite cardinal is an aleph.  ``retract(generalized_continuum_hypothesis())``
withdraws it, and the formal powers and formal suprema return: ``aleph(2)`` and
``2 ** aleph(0)`` are then incomparable in both directions and their sum keeps both terms.
Both states are exact, and a cardinal normalized under one persists under the other.

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

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage.categories.posets import Posets
from sage.categories.semirings import Semirings
from sage.misc.cachefunc import cached_method
from sage.rings.integer import Integer
from sage.rings.semirings.non_negative_integer_semiring import NN
from sage.structure.coerce_dict import MonoDict
from sage.structure.element import Element
from sage.structure.element_wrapper import ElementWrapper
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation

import sage_categories.sets.category as _sets
import sage_categories.sets.objects as _set_objects
import sage_categories.ordinals.category as _ordinals
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.predicates import Decision, Unknown, UnknownClass
from sage_categories.cat.predicates import AppliedPredicate, Predicate, ask, assume, conjunction, disjunction, established, negation
from sage_categories.ordinals.category import OrdinalObject, Ordinals, bind_cardinals, is_natural_number

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.sets.category import SetMap
    from sage_categories.sets.elements import Datum
    from sage_categories.sets.objects import SetObject

__all__ = [
    "Cardinal",
    "CardinalElement",
    "CardinalityMorphism",
    "CardinalObject",
    "aleph0",
    "cardinality_functor",
    "continuum",
    "generalized_continuum_hypothesis",
    "representative_bijection",
]

# A private expression key: nested tuples of strings and integers only, so caches
# and hashes never compare owned values.
type Key = tuple[str | int | Key, ...]


# =====================================================================================
# The cardinal semiring: the data model, holding two Sage semirings as its components
# =====================================================================================
#
# A cardinal expression is an element of one of two commutative semirings, or a formal
# power or join over them.  The finite part is Sage's ``NN``
# (``sage.rings.semirings.non_negative_integer_semiring``), already an object of
# ``Semirings().Commutative()``; no finite arithmetic is written here.  The aleph part is
# ``AlephSemiring``, in which both operations are the maximum.  ``CardinalSemiring`` holds
# the two, delegates each pure case to its component, and case-matches only the mixed
# cases, exponentiation, and the joins.
#
# No ring-like carrier can hold this model, so none should be proposed later.
# ``Cardinal.mul_eq_max`` makes every infinite cardinal a multiplicative idempotent, and
# the only idempotents of an integral domain are ``0`` and ``1``.  Encoding the alephs into
# a polynomial ring, into ``SR``, or into SymPy's number tower therefore identifies every
# infinite cardinal with one of those two, collapsing the model.  Idempotent addition rules
# out the same carriers for ``Cardinal.add_eq_max``.  Sage has no semilattice object to
# reuse, and ``TropicalSemiring`` keeps ordinary addition as its multiplication, so the
# aleph component below is the residue that no library supplies.


# ``generalized_continuum_hypothesis()``: ``2 ** aleph(a) = aleph(a + 1)`` for every
# ordinal ``a``.  It is a proposition, not an axiom of the arithmetic: the session records
# it and ``ask`` reads it (POL-ASSUME-002, POL-ASSUME-004).  This module assumes it below,
# so the package's own default state has it; ``retract`` withdraws it and the exponents
# return to the formal powers and joins that ZFC alone supports.  It carries no arguments
# and records no decision, so nothing about it is cached.
generalized_continuum_hypothesis: Predicate = Predicate("generalized_continuum_hypothesis", 0, False)

assume(generalized_continuum_hypothesis())


class AlephElement(ElementWrapper):
    """``aleph(alpha)``, wrapping the ordinal index it is retained by."""

    def _add_(self, other: AlephElement) -> AlephElement:
        """``Cardinal.add_eq_max``: the sum of two infinite cardinals is the larger."""
        return self.parent().maximum(self, other)

    # ``Cardinal.mul_eq_max``: the product of two infinite cardinals is the larger.
    _mul_ = _add_

    def _repr_(self) -> str:
        return f"ℵ_{self.value}"


class AlephSemiring(UniqueRepresentation, Parent):
    """The alephs under maximum, indexed by ``Ordinals()``.

    Both operations are the maximum on the ordinal index, so this is a commutative
    idempotent semiring whose least element ``aleph_0`` is the identity of each of them.
    Its order is the decidable total order of ``Ordinals()`` (``Cardinal.aleph_le_aleph``).

    Its elements wrap owned ordinals, so ``==`` on two of them is the ordinal proposition
    and ``ask`` decides it; the axioms of the algebra are machine-checked one level up, on
    the cardinal semiring, whose values these are.
    """

    Element = AlephElement

    def __init__(self) -> None:
        Parent.__init__(self, category=Semirings().Commutative() & Posets())

    def _element_constructor_(self, index: OrdinalObject | int) -> AlephElement:
        return self.element_class(self, Ordinals()(index))

    @cached_method
    def zero(self) -> AlephElement:
        """``aleph_0``, the least aleph and therefore the identity of the maximum."""
        return self(0)

    one = zero

    def le(self, first: AlephElement, second: AlephElement) -> Decision:
        """``Cardinal.aleph_le_aleph``: alephs are ordered by their ordinal indices (inspected 2026-08-26)."""
        return ask(first.value <= second.value)

    def maximum(self, first: AlephElement, second: AlephElement) -> AlephElement:
        decision = self.le(first, second)
        assert decision is not Unknown, f"the ordinal indices of {first!r} and {second!r} are incomparable"
        return second if decision else first

    def _repr_(self) -> str:
        return "Aleph semiring"


@dataclass(frozen=True, eq=False, slots=True)
class Power:
    """A cardinal power that no collapse rule evaluates."""

    base: CardinalValue
    exponent: CardinalValue


@dataclass(frozen=True, eq=False, slots=True)
class Join:
    """A finite formal supremum: an antichain of the cardinal order, understood as its own maximum."""

    terms: tuple[CardinalValue, ...]


def _key_order(cardinal: CardinalValue) -> tuple[tuple[int, int | str], ...]:
    """A total order on expression keys, used only to make reduction deterministic.

    This orders *expressions*, never cardinals: the order on cardinals is
    ``CardinalSemiring.le``, which answers ``Unknown`` where ZFC does not decide.
    Reduction to a maximal antichain must visit its candidates in some fixed order, and
    that order carries no mathematical claim.

    A key is a nested tuple of strings and integers, so its parts are ordered by kind
    first and value second; comparing the parts directly would raise on a string
    against an integer.
    """

    def parts(key: Key) -> tuple[tuple[int, int | str], ...]:
        ordered: list[tuple[int, int | str]] = []
        for part in key:
            if isinstance(part, tuple):
                ordered.extend(parts(part))
            else:
                ordered.append((0, part) if isinstance(part, int) else (1, part))
        return tuple(ordered)

    return parts(cardinal._key)


class CardinalValue(Element):
    """One normalized cardinal expression: an element of ``NN``, of the aleph semiring, or a formal power or join."""

    def __init__(self, parent: CardinalSemiring, key: Key, value: Integer | AlephElement | Power | Join) -> None:
        self._key = key
        self._value = value
        Element.__init__(self, parent)

    def _add_(self, other: CardinalValue) -> CardinalValue:
        return self.parent().add(self, other)

    def _mul_(self, other: CardinalValue) -> CardinalValue:
        return self.parent().multiply(self, other)

    def __pow__(self, exponent: CardinalValue | int) -> CardinalValue:
        """``kappa ** lambda``; a natural number exponent is the finite cardinal it names, which is what the monoid power of ``Semirings()`` supplies."""
        match exponent:
            case CardinalValue():
                return self.parent().power(self, exponent)
        return self.parent().power(self, self.parent().finite(exponent))

    def aleph_index(self) -> OrdinalObject:
        """The ordinal index of an aleph, retained by the wrapper the aleph semiring constructed."""
        match self._value:
            case AlephElement():
                return self._value.value
        raise AssertionError(f"{self!r} is not an aleph")

    def finite_value(self) -> int:
        """The natural number of a finite cardinal, at the private computation boundary."""
        match self._value:
            case Integer():
                return int(self._value)
        raise AssertionError(f"{self!r} is not a finite cardinal")

    def __reduce__(self) -> tuple[Callable[[Key], CardinalValue], tuple[Key]]:
        """A cardinal is interned, so its pickle names its key and the round trip returns the same object."""
        return (_retained_cardinal, (self._key,))

    def __hash__(self) -> int:
        return hash(self._key)

    def _repr_(self) -> str:
        match self._value:
            case Power(base, exponent):
                return f"({base!r})^({exponent!r})"
            case Join(terms):
                return "sup(" + ", ".join(map(repr, terms)) + ")"
        return repr(self._value)


def _retained_cardinal(key: Key) -> CardinalValue:
    """The interned cardinal at ``key``; the pickle of a cardinal names this."""
    return CardinalSemiring().retained(key)


class CardinalSemiring(UniqueRepresentation, Parent):
    """The cardinal semiring, holding ``NN`` and the aleph semiring as its two components.

    Every pure case is the held component's own operation: a finite pair is ``NN``'s and an
    aleph pair is the aleph semiring's.  What remains here is the mixed cases,
    exponentiation, and the joins, which are where an expression stays formal.

    The declared order can remain undecided. The owned order operation returns a proposition.
    """

    Element = CardinalValue

    def __init__(self) -> None:
        Parent.__init__(self, category=Semirings().Commutative() & Posets())
        self._finite = NN
        self._alephs = AlephSemiring()
        self._values: dict[Key, CardinalValue] = {}

    # -- construction, interned by expression -------------------------------------

    def _retain(self, key: Key, value: Integer | AlephElement | Power | Join) -> CardinalValue:
        if key not in self._values:
            self._values[key] = self.element_class(self, key, value)
        return self._values[key]

    def retained(self, key: Key) -> CardinalValue:
        assert key in self._values, f"no cardinal is retained at the key {key!r}"
        return self._values[key]

    def _element_constructor_(self, value: int) -> CardinalValue:
        return self.finite(value)

    def finite(self, value: int) -> CardinalValue:
        """The finite cardinal ``n``, constructed by ``NN``, which rejects a negative or non-integral value."""
        member = self._finite(value)
        return self._retain(("finite", int(member)), member)

    def aleph(self, index: OrdinalObject | int) -> CardinalValue:
        """``aleph(alpha)`` for an ordinal index (Mathlib ``Cardinal.aleph``)."""
        member = self._alephs(index)
        return self._retain(("aleph", member.value._expression_key_()), member)

    @cached_method
    def zero(self) -> CardinalValue:
        return self.finite(0)

    @cached_method
    def one(self) -> CardinalValue:
        return self.finite(1)

    def some_elements(self) -> list[CardinalValue]:
        """Two finite cardinals, an aleph, and a power that stays formal: one specimen of each expression form."""
        return [self.zero(), self.one(), self.finite(2), self.aleph(0), self.power(self.finite(2), self.aleph(0))]

    # -- the exact decisions the expressions support ------------------------------

    def is_finite(self, cardinal: CardinalValue) -> Decision:
        match cardinal._value:
            case AlephElement() | Power():
                return False
            case Join(terms):
                return ask(conjunction(self.is_finite(term) for term in terms))
        return True

    def is_countable(self, cardinal: CardinalValue) -> Decision:
        match cardinal._value:
            case AlephElement():
                # Cardinal.aleph0_lt_aleph: aleph(o) is uncountable exactly when 0 < o.
                return ask(cardinal.aleph_index() == 0)
            case Power():
                # Cardinal.cantor': a < b ** a for 1 < b, so 2 ** (infinite) exceeds aleph0.
                return False
            case Join(terms):
                return ask(conjunction(self.is_countable(term) for term in terms))
        return True

    def _established_finite(self, cardinal: CardinalValue) -> bool:
        """Whether finiteness is established, which is what gates an exact arithmetic rule.

        Not the mathematical question: that is ``Cardinal().Finite()``'s predicate, and it
        can be undecided.  A caller uses this to select a normalization rule that needs
        finite operands and otherwise keeps the expression symbolic (POL-MATH-042).
        """
        return established(self.is_finite(cardinal))

    def le(self, first: CardinalValue, second: CardinalValue) -> Decision:
        """``kappa <= lambda`` by the algebra of the normalized expressions.

        This is the exact handler of ``Mor(Cardinal()).Monomorphisms()(kappa, lambda).is_inhabited()``:
        ``Cardinal.le_def`` identifies that inhabitation with this order, and each rule
        below cites the theorem that decides its case.  A pair that no rule reaches is
        ``Unknown``, which is what ZFC leaves open.
        """
        if first is second:
            return True
        match first._value, second._value:
            case Join(terms), _:
                # Cardinal.sup_le_iff: sup T <= b exactly when every term is (inspected 2026-08-28).
                return ask(conjunction(self.le(term, second) for term in terms))
            case _, Join(terms):
                # A finite supremum in the linear order of cardinals is its maximum, so
                # a <= sup T exactly when some term dominates a (Mathlib ``le_max_iff``
                # with ``Cardinal.linearOrder``; inspected 2026-08-28).
                return ask(disjunction(self.le(first, term) for term in terms))
        if self._established_finite(first) and self._established_finite(second):
            return first._value <= second._value  # NN
        if self._established_finite(first):
            return True
        if self._established_finite(second):
            return False
        match first._value, second._value:
            case AlephElement(), AlephElement():
                return self._alephs.le(first._value, second._value)  # the aleph semiring
        match first._value:
            case AlephElement():
                # Cardinal.aleph0_le_mk_iff: aleph0 <= c exactly when c is infinite (inspected 2026-08-28).
                if established(first.aleph_index() == 0):
                    return True
                # Cardinal.aleph_one_le_iff: aleph1 <= c exactly when aleph0 < c (inspected 2026-08-28).
                if established(first.aleph_index() == 1) and established(negation(self.is_countable(second))):
                    return True
            case Power(base, exponent):
                # Cardinal.cantor': b ** a > a for 1 < b, so b ** a is not below anything below a.
                if established(self.le(self.finite(2), base)) and established(self.le(second, exponent)):
                    return False
        match second._value:
            case Power(base, exponent):
                if established(self.le(first, base)):
                    return True
                # Cardinal.cantor': the exponent is below a power with base at least two.
                if established(self.le(self.finite(2), base)) and established(self.le(first, exponent)):
                    return True
                match first._value:
                    case Power(first_base, first_exponent):
                        # Cardinal.power_le_power_right (a <= b gives a ** c <= b ** c) then
                        # Cardinal.power_le_power_left (a != 0 and b <= c give a ** b <= a ** c);
                        # a retained base is at least two, so it is nonzero (inspected 2026-08-28).
                        if established(self.le(first_base, base)) and established(self.le(first_exponent, exponent)):
                            return True
        return Unknown

    # -- arithmetic: each pure case is the held component's own operation -----------

    def add(self, first: CardinalValue, second: CardinalValue) -> CardinalValue:
        if self._established_finite(first) and self._established_finite(second):
            return self.finite(first._value + second._value)  # NN
        match first._value, second._value:
            case AlephElement(), AlephElement():
                return self.aleph((first._value + second._value).value)  # the aleph semiring
        # Cardinal.add_eq_max: an infinite summand absorbs a smaller one.
        if self._established_finite(first):
            return second
        if self._established_finite(second):
            return first
        return self.join(first, second)

    def multiply(self, first: CardinalValue, second: CardinalValue) -> CardinalValue:
        if self._established_finite(first) and self._established_finite(second):
            return self.finite(first._value * second._value)  # NN
        if first is self.zero() or second is self.zero():
            return self.zero()
        match first._value, second._value:
            case AlephElement(), AlephElement():
                return self.aleph((first._value * second._value).value)  # the aleph semiring
        # Cardinal.mul_eq_max: a positive finite factor is absorbed by an infinite one.
        if self._established_finite(first):
            return second
        if self._established_finite(second):
            return first
        return self.join(first, second)

    def power(self, base: CardinalValue, exponent: CardinalValue) -> CardinalValue:
        if exponent is self.zero():
            return self.one()
        if base is self.zero() or base is self.one():
            return base
        if self._established_finite(base) and self._established_finite(exponent):
            return self.finite(base._value**exponent._value)  # NN
        if self._established_finite(exponent):
            # Cardinal.power_nat_eq: c ** n = c for infinite c and n >= 1.
            return base
        match base._value, exponent._value:
            case Power(inner_base, inner_exponent), _:
                # (a ** b) ** c = a ** (b * c).
                return self.power(inner_base, self.multiply(inner_exponent, exponent))
            case Join(terms), _:
                return self.join(*(self.power(term, exponent) for term in terms))
            case _, Join(terms):
                # ``k ** sup T = sup {k ** t}``: a finite supremum of cardinals is its
                # maximum, and ``k ** -`` is monotone (Mathlib ``Cardinal.power_le_power_left``;
                # inspected 2026-08-28).
                return self.join(*(self.power(base, term) for term in terms))
        if established(generalized_continuum_hypothesis()):
            decided = self._power_under_gch(base, exponent)
            if decided is not Unknown:
                return decided
        if self._established_finite(base):
            # Cardinal.nat_power_eq: n ** c = 2 ** c for finite n >= 2 and infinite c.
            base = self.finite(2)
        elif established(self.le(base, exponent)):
            # Cardinal.power_eq_two_power: a ** c = 2 ** c for 2 <= a <= c and infinite c
            # (inspected 2026-08-27); in particular c ** c = 2 ** c (Cardinal.power_self_eq).
            base = self.finite(2)
        return self._retain(("power", base._key, exponent._key), Power(base, exponent))

    def _power_under_gch(self, base: CardinalValue, exponent: CardinalValue) -> CardinalValue | UnknownClass:
        """``aleph(a) ** aleph(b)`` where the generalized continuum hypothesis decides it.

        For ordinals ``a`` and ``b`` the hypothesis gives
        ``aleph(a) ** aleph(b) = aleph(b + 1)`` when ``a <= b + 1``; and when
        ``b + 1 < a``, ``aleph(a)`` if ``aleph(b) < cf(aleph(a))`` and ``aleph(a + 1)``
        otherwise (Wikipedia, "Continuum hypothesis", section "Implications of GCH for
        cardinal exponentiation", after Hayden and Kennison, *Zermelo-Fraenkel Set
        Theory*, page 147; inspected 2026-08-28).  A finite base of at least two has the
        power of two (``Cardinal.nat_power_eq``), which is ``aleph(b + 1)`` by the
        hypothesis itself.

        A cofinality the ordinal expression does not establish leaves the power formal.
        """
        match base._value, exponent._value:
            case Integer(), AlephElement():
                return self.aleph(exponent.aleph_index() + 1)
            case AlephElement(), AlephElement():
                index, exponent_index = base.aleph_index(), exponent.aleph_index()
                if established(index <= exponent_index + 1):
                    return self.aleph(exponent_index + 1)
                cofinality = Ordinals().omega(index).cofinality()
                if cofinality is Unknown:
                    return Unknown
                if exponent is not cofinality._value and established(self.le(exponent, cofinality._value)):
                    return base
                if established(self.le(cofinality._value, exponent)):
                    return self.aleph(index + 1)
        return Unknown

    def join(self, *cardinals: CardinalValue) -> CardinalValue:
        """The finite formal supremum, with dominated terms removed."""
        terms: list[CardinalValue] = []
        for cardinal in cardinals:
            match cardinal._value:
                case Join(inner):
                    terms.extend(inner)
                case _:
                    terms.append(cardinal)
        assert terms
        maximal: list[CardinalValue] = []
        for candidate in sorted(terms, key=_key_order):
            if any(established(self.le(candidate, term)) for term in maximal):
                continue
            maximal = [term for term in maximal if not established(self.le(term, candidate))]
            maximal.append(candidate)
        if len(maximal) == 1:
            return maximal[0]
        return self._retain(("supremum", tuple(term._key for term in maximal)), Join(tuple(maximal)))

    def _repr_(self) -> str:
        return "Cardinal semiring"


# =====================================================================================
# ``Cardinal()``: the category whose objects are these expressions
# =====================================================================================


@dataclass(frozen=True, eq=False, slots=True)
class CardinalObjectData:
    """The cardinal-semiring value introduced by ``Cardinal()``."""

    value: CardinalValue


@dataclass(frozen=True, eq=False, slots=True)
class CardinalMorphismData:
    """The set map state introduced by a morphism of ``Cardinal()``."""

    set_map: SetMap


class CardinalObjectDeclaration:
    """An exact cardinal, retained by its normalized expression in the cardinal semiring."""

    def __init__(self, data: CardinalObjectData) -> None:
        self._value = data.value
        super().__init__()

    def aleph_index(self) -> OrdinalObject:
        """The ordinal index of an aleph, retained by identity at construction."""
        return self._value.aleph_index()

    def _finite_value_(self) -> int:
        """The natural number of a finite cardinal, at the private computation boundary."""
        return self._value.finite_value()

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
        """``kappa >= lambda``: an injection ``R_lambda -> R_kappa`` exists (Mathlib ``Cardinal.le_def``).

        Stated directly rather than as ``Cardinal()(other) <= self``.  A refined
        cardinal's class is a proper subclass of a plain one's, and for those Python
        tries the reflected operator first, so the two spellings called each other.
        """
        cardinals = Cardinal()
        return cardinals.morphism_category(1).Monomorphisms()(cardinals(other), self).is_inhabited()

    def __gt__(self, other: CardinalObject | int) -> AppliedPredicate:
        return less_than(Cardinal()(other), self)

    def __repr__(self) -> str:
        return repr(self._value)


class CardinalMorphismDeclaration:
    """A morphism ``kappa -> lambda`` of ``Cardinal()``: a function between the representatives, retained as a set map."""

    def __init__(self, data: CardinalMorphismData) -> None:
        self._set_map = data.set_map
        super().__init__()

    def __repr__(self) -> str:
        return f"CardinalityMorphism({self.domain()!r} -> {self.codomain()!r})"


# ``less_than(kappa, lambda)``: ``kappa <= lambda`` and not ``kappa == lambda``.
less_than: Predicate = Predicate("cardinal_less_than", 2, True)


class CardinalCategory(Category[[MorphismCategory.ObjectType], []]):
    """The skeletal category of cardinal representatives; its morphisms are the functions between representatives."""

    ObjectType = CardinalObjectDeclaration
    MorphismType = CardinalMorphismDeclaration

    class ElementType:
        """A generalized element of a cardinal; no local operation."""

    def __init__(self) -> None:
        self._semiring = CardinalSemiring()
        self._cardinals: dict[Key, CardinalObject] = {}
        self._representatives: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(self._equal)
        less_than.register_handler(self._less_than)
        self._countable_cardinals = PropertySubcategory(self, "Countable", ())
        self._infinite_cardinals = PropertySubcategory(self, "Infinite", ())
        self._finite_cardinals = PropertySubcategory(self, "Finite", (self._countable_cardinals,))
        self._uncountable_cardinals = PropertySubcategory(self, "Uncountable", (self._infinite_cardinals,))
        self._finite_cardinals.predicate().register_handler(self._is_finite)
        self._infinite_cardinals.predicate().register_handler(lambda cardinal: ask(negation(self._is_finite(cardinal))))
        self._countable_cardinals.predicate().register_handler(self._is_countable)
        self._uncountable_cardinals.predicate().register_handler(lambda cardinal: ask(negation(self._is_countable(cardinal))))

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

    @cached_method
    def representative_functor(self) -> Functor:
        """The functor ``Cardinal() -> Sets()`` sending ``kappa`` to ``R_kappa`` and a cardinal morphism to its map, retained once.

        Fully faithful by the definition of the morphisms of ``Cardinal()``: the skeleton
        monomorphism (Mathlib ``CategoryTheory.fromSkeleton``, an equivalence; inspected 2026-08-27).
        """
        return Fun(self, _sets.Sets()).FullyFaithful()(self.representative, lambda morphism: morphism._set_map)

    def representative(self, cardinal: CardinalObject) -> SetObject:
        """The selected representative set ``R_kappa``, one per cardinal."""
        return self.representative_functor().on_object(cardinal)

    def _select_representative(self, cardinal: CardinalObject, data: CardinalObjectData) -> SetObject:
        sets = _sets.Sets()
        match data.value._value:
            case Integer() as size:
                # #[n - 1] = #{0, ..., n - 1} = n: Mathlib ``Cardinal.mk_fin`` (inspected 2026-08-27).
                return sets.Finite()._from_enumeration(tuple(range(size)), cardinal)

        def no_datum(datum: Datum) -> Decision:
            return Unknown

        return sets.rule_valued(no_datum, cardinal)

    # -- construction, cached by expression ---------------------------------------

    def _retain(self, value: CardinalValue) -> CardinalObject:
        if value._key not in self._cardinals:
            self._cardinals[value._key] = self.ObjectType(category=self, data=CardinalObjectData(value=value))
        return self._cardinals[value._key]

    def __call__(self, value: CardinalObject | int) -> CardinalObject:
        """``Cardinal()(n)`` for a nonnegative integer; a cardinal is returned unchanged.

        A finite cardinal is a natural number, and its Python integer keys the
        expression and sizes the representative, so the constructor states integrality
        here instead of failing later at the representative.
        """
        if value in self:
            return value
        assert is_natural_number(value), f"{value!r} is not a cardinal"
        return self._retain(self._semiring.finite(value))

    def aleph(self, index: OrdinalObject | int) -> CardinalObject:
        """``aleph(alpha)`` for an ordinal index; an ``int`` is the finite-ordinal convenience (Mathlib ``Cardinal.aleph``)."""
        return self._retain(self._semiring.aleph(index))

    def zero(self) -> CardinalObject:
        return self(0)

    def one(self) -> CardinalObject:
        return self(1)

    def supremum(self, *cardinals: CardinalObject) -> CardinalObject:
        """The finite formal supremum, with dominated terms removed."""
        return self._retain(self._semiring.join(*(cardinal._value for cardinal in cardinals)))

    def sum(self, first: CardinalObject, second: CardinalObject) -> CardinalObject:
        return self._retain(first._value + second._value)

    def product(self, first: CardinalObject, second: CardinalObject) -> CardinalObject:
        return self._retain(first._value * second._value)

    def power(self, base: CardinalObject, exponent: CardinalObject) -> CardinalObject:
        return self._retain(base._value**exponent._value)

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
                return ask(disjunction((self._equal(source, self(0)), negation(self._equal(target, self(0))))))
            case (root,) if root is morphisms.Monomorphisms():
                return self._at_most(source, target)
            case (root,) if root is morphisms.Isomorphisms():
                return self._equal(source, target)
        return Unknown

    # -- exact decisions -----------------------------------------------------------

    def _is_finite(self, cardinal: CardinalObject) -> Decision:
        return self._semiring.is_finite(cardinal._value)

    def _is_countable(self, cardinal: CardinalObject) -> Decision:
        return self._semiring.is_countable(cardinal._value)

    def _equal(self, first: CategoryOfCategories.ElementType, candidate: Any) -> Decision:
        if first not in self:
            return Unknown
        if candidate in self:
            second = candidate
        elif not hasattr(candidate, "_is_object") and is_natural_number(candidate):
            second = self(candidate)
        else:
            return Unknown
        if first is second:
            return True
        # Cardinal.le_antisymm: two cardinals are equal exactly when each is at most the
        # other (inspected 2026-08-28).
        return ask(conjunction((self._at_most(first, second), self._at_most(second, first))))

    def _at_most(self, first: CardinalObject, second: CardinalObject) -> Decision:
        return self._semiring.le(first._value, second._value)

    def _less_than(self, first: CardinalObject, second: CardinalObject) -> Decision:
        if first is second:
            return False
        if established(self._at_most(first, second)):
            return ask(~(first == second))
        if established(self._at_most(second, first)):
            return False
        return Unknown

    def __repr__(self) -> str:
        return "Cardinal"


_CARDINAL = CardinalCategory()
CardinalObject = _CARDINAL.ObjectType
CardinalElement = _CARDINAL.ElementType
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


# ``ordinals/category.py`` is imported above and names ``CardinalObject`` in a
# declared signature; this module is where that name exists, so it closes the
# cluster (``ordinals.category.bind_cardinals``).
bind_cardinals()
