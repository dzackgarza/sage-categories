"""``Ordinals()``: exact ordinal expressions with Hessenberg natural arithmetic (``specs/ordinals.md``).

An ordinal is an object of ``Ordinals()``, retained once by its normalized
expression: a finite ordinal, an initial ordinal ``omega(alpha)``, a Hessenberg
natural sum or product, or an ordinary ordinal sum, product, or power that no
normalization rule evaluates.  Python ``+`` and ``*`` are the natural operations
(Mathlib ``Ordinal.nadd`` and ``Ordinal.nmul``; ``NatOrdinal`` is a commutative
semiring through ``NatOrdinal.instCommSemiring``, Mathlib
``SetTheory.Ordinal.NaturalOps``; inspected 2026-08-26); the noncommutative
ordinary operations have explicit names.

Normalization, exactly as ``specs/ordinals.md`` states it:

- a natural sum flattens nested sums, combines its finite terms, drops zero, and
  sorts its symbolic terms (``Ordinal.nadd_comm``, ``Ordinal.nadd_nat``, and the
  semiring laws of ``NatOrdinal``);
- a natural product distributes over natural sums (``Ordinal.nmul_nadd``,
  ``Ordinal.nadd_nmul``), flattens, multiplies its finite factors, drops one
  (``Ordinal.nmul_one``), is zero when a factor is zero, and sorts;
- ordinary sums, products, and powers evaluate finite inputs (``Ordinal.natCast_mul``,
  ``Ordinal.natCast_opow``, ``Nat.cast_add``), simplify by the unit laws and
  ``Ordinal.opow_zero``, ``Ordinal.zero_opow``, ``Ordinal.one_opow``
  (``SetTheory.Ordinal.Exponential``), and otherwise remain symbolic.

Every nonfinite expression is at least ``omega0``: an initial ordinal by
``Ordinal.omega0_le_omega``, and each symbolic sum, product, or power dominates a
nonfinite term (``Ordinal.le_self_nadd``, ``Ordinal.add_le_nadd``,
``Ordinal.mul_le_nmul``).  Hence finiteness is the expression kind, and the exact
order handler decides: expression equality; order between finite ordinals; every
finite ordinal below every nonfinite one (``Ordinal.natCast_lt_omega0``); order
between initial ordinals through their indices (``Ordinal.omega_le_omega``,
``Ordinal.omega_lt_omega``, Mathlib ``SetTheory.Cardinal.Aleph``).  Equality is
``True`` by expression, ``False`` when the order handler separates the two
expressions strictly, and ``Unknown`` otherwise: a symbolic expression can equal
another (``1 +o omega0`` is ``omega0`` by ``Ordinal.one_add_omega0``), so distinct
expressions never decide inequality by themselves.
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from functools import reduce
from typing import TYPE_CHECKING

from sage.rings.integer_ring import ZZ as _integer_ring

from sage_categories.cat.category import Category
from sage_categories.cat.predicates import Decision, Unknown, UnknownClass
from sage_categories.cat.predicates import AppliedPredicate, Predicate, predicate

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.sets.cardinals import CardinalObject

__all__ = [
    "OrdinalObject",
    "OrdinalOrder",
    "Ordinals",
    "OrdinalsCategory",
    "at_most",
    "bind_cardinals",
    "initial",
    "less_than",
    "omega",
    "omega0",
    "ordinal",
]


def bind_cardinals() -> None:
    """Bind ``CardinalObject`` in this module, once ``sets/cardinals.py`` exists.

    ``OrdinalObject.cardinality()`` names a cardinal, and the kernel evaluates a
    declared annotation with ``eval_str`` against the declaring module
    (POL-KERNEL-021), so the name must resolve here.  Cardinals are indexed by
    ordinals, so this module is imported first and cannot import them; the
    cardinals module closes the cluster by calling this, exactly as
    ``cat/category.py`` closes the ``Cat()`` cluster in ``bootstrap``.
    """
    global CardinalObject

    from sage_categories.sets.cardinals import CardinalObject


# A private expression key: nested tuples of strings and integers only, so caches
# and hashes never compare owned values.
type Key = tuple[Hashable, ...]


@dataclass(frozen=True, eq=False, slots=True)
class OrdinalObjectData:
    """The normalized expression state introduced by ``Ordinals()``."""

    key: Key
    terms: tuple[OrdinalObject, ...]


class OrdinalObjectDeclaration:
    """An exact ordinal, retained by its normalized expression."""

    def __init__(self, data: OrdinalObjectData) -> None:
        self._key = data.key
        self._terms = data.terms
        super().__init__()

    def _kind_(self) -> str:
        return self._key[0]

    def _expression_key_(self) -> Key:
        """The normalized expression that identifies this ordinal."""
        return self._key

    def _terms_(self) -> tuple[OrdinalObject, ...]:
        return self._terms

    def _finite_value_(self) -> int:
        assert self._kind_() == "finite"
        return self._key[1]

    def is_initial(self) -> AppliedPredicate:
        return initial(self)

    def initial_index(self) -> OrdinalObject:
        assert self._kind_() == "initial", f"{self!r} is not an initial ordinal"
        return self._terms[0]

    def cardinality(self) -> CardinalObject:
        """The cardinal of this ordinal (``specs/ordinals.md``, "Cardinality of ordinals").

        Each rule is an inspected Mathlib theorem (inspected 2026-08-26):
        ``Ordinal.card_nat``; ``Ordinal.card_omega`` (``SetTheory.Cardinal.Aleph``);
        ``Ordinal.card_add`` and ``Ordinal.card_mul``, which the natural operations
        share because a natural sum or product is the order type of a well-order on
        the same underlying set as the ordinary one (``Ordinal.nadd``,
        ``Ordinal.nmul`` in ``SetTheory.Ordinal.NaturalOps``); and for a symbolic
        power ``Ordinal.card_opow_eq_of_omega0_le_left`` and
        ``Ordinal.card_opow_eq_of_omega0_le_right`` (``SetTheory.Cardinal.Ordinal``):
        ``|a ^o b| = max(|a|, |b|)`` when ``omega0 <= a`` and ``0 < b``, or
        ``1 < a`` and ``omega0 <= b``, which are exactly the symbolic cases.
        """
        from sage_categories.sets.cardinals import Cardinal

        cardinals = Cardinal()
        match self._kind_():
            case "finite":
                return cardinals(self._finite_value_())
            case "initial":
                return cardinals.aleph(self.initial_index())
            case "natural_sum" | "ordinal_sum":
                return reduce(cardinals.sum, (term.cardinality() for term in self._terms))
            case "natural_product" | "ordinal_product":
                return reduce(cardinals.product, (term.cardinality() for term in self._terms))
        base, exponent = self._terms
        return cardinals.supremum(base.cardinality(), exponent.cardinality())

    def cofinality(self) -> CardinalObject | UnknownClass:
        """``cf(alpha)``, the cofinality of this ordinal, as a cardinal (Mathlib ``Ordinal.cof``; inspected 2026-08-28).

        Each rule is an inspected theorem: ``cof 0 = 0`` (``Ordinal.cof_zero``) and
        ``cof (o + 1) = 1`` (``Ordinal.cof_add_one``), which covers a positive finite
        ordinal and a natural sum with a nonzero finite term, since a natural sum with a
        finite ordinal is the ordinary one (``Ordinal.nadd_nat``); ``cof omega_0 = aleph0``
        (``Ordinal.cof_omega0``); ``aleph(b + 1)`` is regular
        (``Cardinal.isRegular_aleph_add_one``), and a regular cardinal is the cofinality of
        its own initial ordinal (``Cardinal.isRegular_iff`` with ``Ordinal.cof_le_card``),
        so ``cof omega_n = aleph(n)`` for ``n >= 1``; and ``cof omega_b = cof b`` for a
        limit index ``b`` (``Ordinal.cof_omega``), whose hypothesis an initial ordinal
        satisfies by ``Cardinal.isSuccLimit_ord`` at ``aleph0 <= aleph(g)``.

        Any other expression is ``Unknown``: the shape that would select a rule is not
        established.
        """
        from sage_categories.sets.cardinals import Cardinal

        cardinals = Cardinal()
        match self._kind_():
            case "finite":
                return cardinals(0) if self._finite_value_() == 0 else cardinals(1)
            case "natural_sum" if any(term._kind_() == "finite" for term in self._terms_()):
                return cardinals(1)
            case "initial":
                index = self.initial_index()
                match index._kind_():
                    case "finite":
                        return cardinals.aleph(0) if index._finite_value_() == 0 else cardinals.aleph(index)
                    case "initial":
                        return index.cofinality()
        return Unknown

    def __add__(self, other: OrdinalObject | int) -> OrdinalObject:
        return Ordinals().natural_sum(self, Ordinals()(other))

    def __radd__(self, other: int) -> OrdinalObject:
        return Ordinals().natural_sum(Ordinals()(other), self)

    def __mul__(self, other: OrdinalObject | int) -> OrdinalObject:
        return Ordinals().natural_product(self, Ordinals()(other))

    def __rmul__(self, other: int) -> OrdinalObject:
        return Ordinals().natural_product(Ordinals()(other), self)

    def ordinal_sum(self, other: OrdinalObject | int) -> OrdinalObject:
        return Ordinals().ordinal_sum(self, Ordinals()(other))

    def ordinal_product(self, other: OrdinalObject | int) -> OrdinalObject:
        return Ordinals().ordinal_product(self, Ordinals()(other))

    def ordinal_power(self, exponent: OrdinalObject | int) -> OrdinalObject:
        return Ordinals().ordinal_power(self, Ordinals()(exponent))

    def __le__(self, other: OrdinalObject | int) -> AppliedPredicate:
        return at_most(self, Ordinals()(other))

    def __lt__(self, other: OrdinalObject | int) -> AppliedPredicate:
        return less_than(self, Ordinals()(other))

    def __ge__(self, other: OrdinalObject | int) -> AppliedPredicate:
        return at_most(Ordinals()(other), self)

    def __gt__(self, other: OrdinalObject | int) -> AppliedPredicate:
        return less_than(Ordinals()(other), self)

    def __hash__(self) -> int:
        return hash(self._key)

    def __repr__(self) -> str:
        match self._kind_():
            case "finite":
                return str(self._finite_value_())
            case "initial":
                return f"ω_{self.initial_index()!r}"
            case "natural_sum":
                return " # ".join(map(repr, self._terms))
            case "natural_product":
                return " ⊗ ".join(map(repr, self._terms))
            case "ordinal_sum":
                return f"({self._terms[0]!r} +o {self._terms[1]!r})"
            case "ordinal_product":
                return f"({self._terms[0]!r} *o {self._terms[1]!r})"
        return f"({self._terms[0]!r} ^o {self._terms[1]!r})"


# ``initial(alpha)``: ``alpha`` is an initial ordinal ``omega(beta)``.
initial: Predicate = predicate("ordinal_initial")
# ``at_most(alpha, beta)``: ``alpha <= beta`` in the ordinal order.
at_most: Predicate = predicate("ordinal_at_most")
# ``less_than(alpha, beta)``: ``alpha < beta``.
less_than: Predicate = predicate("ordinal_less_than")


class OrdinalsCategory(Category[[], []]):
    """The category of exact ordinal expressions."""

    ObjectType = OrdinalObjectDeclaration

    class ElementType:
        """A generalized element of an ordinal; no local operation."""

    class MorphismType:
        """A morphism between ordinals; no local operation."""

    def __init__(self) -> None:
        self._ordinals: dict[Key, OrdinalObject] = {}
        super().__init__()
        self._equality.register_handler(self._equal)
        at_most.register_handler(self._at_most)
        less_than.register_handler(self._less_than)
        initial.register_handler(self._initial)

    # -- construction, cached by expression ---------------------------------------

    def _retain(self, key: Key, terms: tuple[OrdinalObject, ...]) -> OrdinalObject:
        if key not in self._ordinals:
            self._ordinals[key] = self.ObjectType(category=self, data=OrdinalObjectData(key=key, terms=terms))
        return self._ordinals[key]

    def __call__(self, value: OrdinalObject | int) -> OrdinalObject:
        """``Ordinals()(n)`` for a nonnegative integer; an ordinal is returned unchanged.

        A finite ordinal is a natural number, so the constructor states integrality as
        a precondition and Sage's exact integer ring decides it.  ``int()`` then only
        normalizes an established integer to the Python integer that keys every finite
        expression; it never truncates a value that is not one.
        """
        if value in self:
            return value
        assert value in _integer_ring and value >= 0, f"{value!r} is not an ordinal"
        return self._retain(("finite", int(value)), ())

    def omega(self, index: OrdinalObject | int) -> OrdinalObject:
        """The initial ordinal ``omega(index)`` (Mathlib ``Ordinal.omega``, ``SetTheory.Cardinal.Aleph``)."""
        ordinal_index = self(index)
        return self._retain(("initial", ordinal_index._expression_key_()), (ordinal_index,))

    def zero(self) -> OrdinalObject:
        return self(0)

    def one(self) -> OrdinalObject:
        return self(1)

    def _equals_finite(self, alpha: OrdinalObject, value: int) -> bool:
        return alpha._kind_() == "finite" and alpha._finite_value_() == value

    def _expression(self, kind: str, terms: tuple[OrdinalObject, ...]) -> OrdinalObject:
        return self._retain((kind, *(term._expression_key_() for term in terms)), terms)

    def natural_sum(self, *summands: OrdinalObject) -> OrdinalObject:
        terms: list[OrdinalObject] = []
        finite_part = 0
        for summand in summands:
            match summand._kind_():
                case "finite":
                    finite_part += summand._finite_value_()
                case "natural_sum":
                    terms.extend(summand._terms_())
                case _:
                    terms.append(summand)
        if finite_part:
            terms.append(self(finite_part))
        if not terms:
            return self.zero()
        terms.sort(key=repr)
        if len(terms) == 1:
            return terms[0]
        return self._expression("natural_sum", tuple(terms))

    def natural_product(self, *factors: OrdinalObject) -> OrdinalObject:
        for index, factor in enumerate(factors):
            if factor._kind_() == "natural_sum":
                preceding, following = factors[:index], factors[index + 1 :]
                return self.natural_sum(*(self.natural_product(*preceding, term, *following) for term in factor._terms_()))
        terms: list[OrdinalObject] = []
        finite_part = 1
        for factor in factors:
            match factor._kind_():
                case "finite":
                    if factor._finite_value_() == 0:
                        return self.zero()
                    finite_part *= factor._finite_value_()
                case "natural_product":
                    terms.extend(factor._terms_())
                case _:
                    terms.append(factor)
        if finite_part != 1 or not terms:
            terms.append(self(finite_part))
        terms.sort(key=repr)
        if len(terms) == 1:
            return terms[0]
        return self._expression("natural_product", tuple(terms))

    def ordinal_sum(self, left: OrdinalObject, right: OrdinalObject) -> OrdinalObject:
        if left._kind_() == "finite" and right._kind_() == "finite":
            return self(left._finite_value_() + right._finite_value_())
        if self._equals_finite(left, 0):
            return right
        if self._equals_finite(right, 0):
            return left
        return self._expression("ordinal_sum", (left, right))

    def ordinal_product(self, left: OrdinalObject, right: OrdinalObject) -> OrdinalObject:
        if left._kind_() == "finite" and right._kind_() == "finite":
            return self(left._finite_value_() * right._finite_value_())
        if self._equals_finite(left, 0) or self._equals_finite(right, 0):
            return self.zero()
        if self._equals_finite(left, 1):
            return right
        if self._equals_finite(right, 1):
            return left
        return self._expression("ordinal_product", (left, right))

    def ordinal_power(self, base: OrdinalObject, exponent: OrdinalObject) -> OrdinalObject:
        if base._kind_() == "finite" and exponent._kind_() == "finite":
            return self(base._finite_value_() ** exponent._finite_value_())
        if self._equals_finite(exponent, 0):
            return self.one()
        if self._equals_finite(base, 0):
            return self.zero()
        if self._equals_finite(base, 1):
            return self.one()
        return self._expression("ordinal_power", (base, exponent))

    # -- exact decisions -----------------------------------------------------------

    def _initial(self, alpha: OrdinalObjectDeclaration, assumptions: Proposition | None = None) -> Decision:
        """An initial-ordinal expression is initial and a finite ordinal is not (``Ordinal.natCast_lt_omega0``,
        ``Ordinal.omega0_le_omega``); a symbolic expression may still equal one, so it is ``Unknown``."""
        match alpha._kind_():
            case "initial":
                return True
            case "finite":
                return False
        return Unknown

    def _equal(self, first: OrdinalObjectDeclaration, second: OrdinalObjectDeclaration, assumptions: Proposition | None = None) -> Decision:
        if first not in self:
            return Unknown
        if first._key == second._key:
            return True
        # Ordinal.le_antisymm: two ordinals are equal exactly when each is at most the
        # other (inspected 2026-08-28).  The two order decisions compose by Kleene's
        # strong conjunction: a strict separation decides inequality, two positive
        # decisions decide equality, and anything else is Unknown.
        forward = self._at_most(first, second, assumptions)
        backward = self._at_most(second, first, assumptions)
        if forward is False or backward is False:
            return False
        if forward is True and backward is True:
            return True
        return Unknown

    def _at_most(self, first: OrdinalObjectDeclaration, second: OrdinalObjectDeclaration, assumptions: Proposition | None = None) -> Decision:
        if first._key == second._key:
            return True
        if first._kind_() == "finite":
            if second._kind_() == "finite":
                return first._finite_value_() <= second._finite_value_()
            return True
        if second._kind_() == "finite":
            return False
        if first._kind_() == "initial" and second._kind_() == "initial":
            return self._at_most(first.initial_index(), second.initial_index())
        return Unknown

    def _less_than(self, first: OrdinalObjectDeclaration, second: OrdinalObjectDeclaration, assumptions: Proposition | None = None) -> Decision:
        # Each ``True`` of ``_at_most`` between distinct expressions is strict: the
        # finite and finite-below-nonfinite cases by definition, the initial case by
        # induction on the indices (``Ordinal.omega_lt_omega``).
        if first._key == second._key:
            return False
        return self._at_most(first, second)

    def __repr__(self) -> str:
        return "Ordinals"


_ORDINALS = OrdinalsCategory()
OrdinalObject = _ORDINALS.ObjectType


def Ordinals() -> OrdinalsCategory:
    """The category of exact ordinals."""
    return _ORDINALS


def ordinal(value: OrdinalObject | int) -> OrdinalObject:
    """``Ordinals()(value)``."""
    return Ordinals()(value)


def omega(index: OrdinalObject | int) -> OrdinalObject:
    """``Ordinals().omega(index)``."""
    return Ordinals().omega(index)


omega0: OrdinalObject = omega(0)
_ORDINAL_ORDER = None


def OrdinalOrder() -> Category:
    """The thin category of the ordinal order (specs/cardinality.md, specs/ordinals.md)."""
    global _ORDINAL_ORDER
    if _ORDINAL_ORDER is None:
        from sage_categories.cat.shapes import Thin

        _ORDINAL_ORDER = Thin(Ordinals(), at_most)
    return _ORDINAL_ORDER
