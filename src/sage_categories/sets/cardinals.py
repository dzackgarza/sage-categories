"""``Cardinal()``: exact cardinal numbers (D01, ``specs/cardinality.md``).

A cardinal is an exact value: a finite cardinal, ``aleph(n)``, a cardinal power,
or a finite formal supremum formed by exact cardinal arithmetic.  There is no
placeholder cardinal and no unknown cardinal; cardinals implement no ``Unknown``
handling.  Construction is cached by expression, so an equal expression returns
the same object.

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
"""

from __future__ import annotations

from typing import Any

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.decisions import Decision, Unknown, decision_and, decision_not
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, ask
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, role_of
from sage_categories.ordinals.category import OrdinalObject, Ordinals

__all__ = ["Cardinal", "CardinalObject", "aleph0", "continuum"]

# A private expression key: nested tuples of strings and integers only, so caches
# and hashes never compare owned values.
type Key = tuple[str | int | Key, ...]


class CardinalObject(ObjectOfCategory):
    """An exact cardinal, retained by its normalized expression."""

    def __init__(self, category: Category, key: Key, terms: tuple[CardinalObject, ...]) -> None:
        super().__init__(category)
        self._key = key
        self._terms = terms

    def kind(self) -> str:
        return self._key[0]

    def terms(self) -> tuple[CardinalObject, ...]:
        return self._terms

    def finite_value(self) -> int:
        assert self.kind() == "finite"
        return self._key[1]

    def aleph_index(self) -> OrdinalObject:
        """The ordinal index of an aleph, retained by identity at construction."""
        assert self.kind() == "aleph"
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
        return at_most(self, Cardinal()(other))

    def __lt__(self, other: CardinalObject | int) -> AppliedPredicate:
        return less_than(self, Cardinal()(other))

    def __ge__(self, other: CardinalObject | int) -> AppliedPredicate:
        return at_most(Cardinal()(other), self)

    def __gt__(self, other: CardinalObject | int) -> AppliedPredicate:
        return less_than(Cardinal()(other), self)

    def __hash__(self) -> int:
        return hash(self._key)

    def __repr__(self) -> str:
        match self.kind():
            case "finite":
                return str(self.finite_value())
            case "aleph":
                return f"ℵ_{self.aleph_index()}"
            case "power":
                base, exponent = self._terms
                return f"({base!r})^({exponent!r})"
        return "sup(" + ", ".join(map(repr, self._terms)) + ")"


# ``at_most(kappa, lambda)``: an injection ``R_kappa -> R_lambda`` exists.
at_most = Predicate("cardinal_at_most", 2, True)
# ``less_than(kappa, lambda)``: ``kappa <= lambda`` and not ``kappa == lambda``.
less_than = Predicate("cardinal_less_than", 2, True)


class CardinalCategory(Category[[], []]):
    """The skeletal category of cardinal representatives; morphisms arrive with the skeletal inclusion."""

    ObjectType = CardinalObject

    class ElementType(ElementOfObject):
        """A generalized element of a cardinal; no local operation."""

    class MorphismType(MorphismOfCategory):
        """A function between cardinal representatives; constructed with the skeletal inclusion into ``Sets()``."""

    def __init__(self) -> None:
        self._cardinals: dict[Key, CardinalObject] = {}
        self._aleph_indices: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(self._equal)
        at_most.register_handler(self._at_most)
        less_than.register_handler(self._less_than)
        countable = PropertySubcategory(self, "Countable", {}, ())
        infinite = PropertySubcategory(self, "Infinite", {}, ())
        finite = PropertySubcategory(self, "Finite", {}, (countable,))
        uncountable = PropertySubcategory(self, "Uncountable", {}, (infinite,))
        finite.predicate().register_handler(self._is_finite)
        infinite.predicate().register_handler(lambda cardinal: decision_not(self._is_finite(cardinal)))
        countable.predicate().register_handler(self._is_countable)
        uncountable.predicate().register_handler(lambda cardinal: decision_not(self._is_countable(cardinal)))
        self._properties.update({"Finite": finite, "Infinite": infinite, "Countable": countable, "Uncountable": uncountable})

    def Finite(self) -> Category:
        return self._properties["Finite"]

    def Infinite(self) -> Category:
        return self._properties["Infinite"]

    def Countable(self) -> Category:
        return self._properties["Countable"]

    def Uncountable(self) -> Category:
        return self._properties["Uncountable"]

    # -- construction, cached by expression ---------------------------------------

    def _retain(self, key: Key, terms: tuple[CardinalObject, ...]) -> CardinalObject:
        if key not in self._cardinals:
            self._cardinals[key] = self.ObjectType(self, key, terms)
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
        key: Key = ("aleph", ordinal_index.expression_key())
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
            terms.extend(cardinal.terms() if cardinal.kind() == "supremum" else (cardinal,))
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
            return self(first.finite_value() + second.finite_value())
        # Cardinal.add_eq_max: an infinite summand absorbs a smaller one.
        if self._finite(first):
            return second
        if self._finite(second):
            return first
        return self.supremum(first, second)

    def product(self, first: CardinalObject, second: CardinalObject) -> CardinalObject:
        if self._finite(first) and self._finite(second):
            return self(first.finite_value() * second.finite_value())
        if self._finite(first) and first.finite_value() == 0 or self._finite(second) and second.finite_value() == 0:
            return self(0)
        # Cardinal.mul_eq_max: a positive finite factor is absorbed by an infinite one.
        if self._finite(first):
            return second
        if self._finite(second):
            return first
        return self.supremum(first, second)

    def power(self, base: CardinalObject, exponent: CardinalObject) -> CardinalObject:
        if self._finite(exponent) and exponent.finite_value() == 0:
            return self(1)
        if self._finite(base) and base.finite_value() in (0, 1):
            return base
        if self._finite(base) and self._finite(exponent):
            return self(base.finite_value() ** exponent.finite_value())
        if self._finite(exponent):
            # Cardinal.power_nat_eq: c ** n = c for infinite c and n >= 1.
            return base
        if base.kind() == "power":
            # (a ** b) ** c = a ** (b * c).
            inner_base, inner_exponent = base.terms()
            return self.power(inner_base, self.product(inner_exponent, exponent))
        if base.kind() == "supremum":
            return self.supremum(*(self.power(term, exponent) for term in base.terms()))
        if self._finite(base):
            # Cardinal.nat_power_eq: n ** c = 2 ** c for finite n >= 2 and infinite c.
            base = self(2)
        return self._retain(("power", base._key, exponent._key), (base, exponent))

    # -- exact decisions -----------------------------------------------------------

    def _is_finite(self, cardinal: CardinalObject) -> Decision:
        match cardinal.kind():
            case "finite":
                return True
            case "aleph" | "power":
                return False
        return all(self._is_finite(term) is True for term in cardinal.terms())

    def _is_countable(self, cardinal: CardinalObject) -> Decision:
        match cardinal.kind():
            case "finite":
                return True
            case "aleph":
                # Cardinal.aleph0_lt_aleph: aleph(o) is uncountable exactly when 0 < o.
                return ask(cardinal.aleph_index() == 0)
            case "power":
                # Cardinal.cantor': a < b ** a for 1 < b, so 2 ** (infinite) exceeds aleph0.
                return False
        return all(self._is_countable(term) is True for term in cardinal.terms())

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
        if first.kind() == "supremum":
            answers = [self._at_most(term, second) for term in first.terms()]
            if all(answer is True for answer in answers):
                return True
            if any(answer is False for answer in answers):
                return False
            return Unknown
        if second.kind() == "supremum":
            if any(self._at_most(first, term) is True for term in second.terms()):
                return True
            return Unknown
        if self._finite(first) and self._finite(second):
            return first.finite_value() <= second.finite_value()
        if self._finite(first):
            return True
        if self._finite(second):
            return False
        if first.kind() == "aleph" and second.kind() == "aleph":
            # Cardinal.aleph_le_aleph: alephs are ordered by their ordinal indices.
            return ask(first.aleph_index() <= second.aleph_index())
        if first.kind() == "aleph" and ask(first.aleph_index() == 0) is True:
            return True
        if first.kind() == "aleph" and ask(first.aleph_index() == 1) is True and self._is_countable(second) is False:
            return True
        if first.kind() == "power":
            base, exponent = first.terms()
            # Cardinal.cantor': b ** a > a for 1 < b, so b ** a is not below anything below a.
            if self._at_most(self(2), base) is True and self._at_most(second, exponent) is True:
                return False
        if second.kind() == "power":
            base, exponent = second.terms()
            if self._at_most(first, base) is True:
                return True
            # Cardinal.cantor': the exponent is below a power with base at least two.
            if self._at_most(self(2), base) is True and self._at_most(first, exponent) is True:
                return True
            if first.kind() == "power":
                first_base, first_exponent = first.terms()
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


def Cardinal() -> CardinalCategory:
    """The category of exact cardinals."""
    return _CARDINAL


aleph0 = Cardinal().aleph(0)
continuum = Cardinal()(2) ** aleph0
