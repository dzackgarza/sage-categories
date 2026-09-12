"""Exact symbolic rational, real, and p-adic fields for infinitary consumers."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from math import inf
from typing import Any, cast

from sympy import false, true
from sympy.ntheory.primetest import isprime

from sage_categories.algebra._certified_commutative_ring import (
    certified_commutative_ring,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import Rings

__all__ = [
    "ExactLocalFieldPresentation",
    "ExactLocalValue",
    "exact_padic_field",
    "exact_rational_field",
    "exact_real_field",
    "prime_indices",
]


@dataclass(frozen=True, slots=True)
class _ExactExpression:
    operation: str
    arguments: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class ExactLocalValue:
    """An exact local value, distinct from any finite-precision approximation."""

    place: str | int
    expression: _ExactExpression

    @staticmethod
    def rational(place: str | int, value: Fraction | int) -> ExactLocalValue:
        return ExactLocalValue(place, _ExactExpression("rational", (Fraction(value),)))

    @staticmethod
    def atom(
        place: str | int,
        name: object,
        valuation: int | None = None,
    ) -> ExactLocalValue:
        return ExactLocalValue(place, _ExactExpression("atom", (name, valuation)))

    def rational_value(self) -> Fraction | None:
        match self.expression.operation:
            case "rational":
                return cast(Fraction, self.expression.arguments[0])
            case "negate":
                value = cast(ExactLocalValue, self.expression.arguments[0]).rational_value()
                return None if value is None else -value
            case "add":
                first = cast(ExactLocalValue, self.expression.arguments[0]).rational_value()
                second = cast(ExactLocalValue, self.expression.arguments[1]).rational_value()
                return None if first is None or second is None else first + second
            case "multiply":
                first = cast(ExactLocalValue, self.expression.arguments[0]).rational_value()
                second = cast(ExactLocalValue, self.expression.arguments[1]).rational_value()
                return None if first is None or second is None else first * second
            case _:
                return None

    def __neg__(self) -> ExactLocalValue:
        rational = self.rational_value()
        match rational:
            case Fraction():
                return ExactLocalValue.rational(self.place, -rational)
            case None:
                return ExactLocalValue(self.place, _ExactExpression("negate", (self,)))

    def __add__(self, other: ExactLocalValue) -> ExactLocalValue:
        assert self.place == other.place
        first, second = self.rational_value(), other.rational_value()
        match first, second:
            case Fraction(), Fraction():
                return ExactLocalValue.rational(self.place, first + second)
            case _:
                return ExactLocalValue(self.place, _ExactExpression("add", (self, other)))

    def __mul__(self, other: ExactLocalValue) -> ExactLocalValue:
        assert self.place == other.place
        first, second = self.rational_value(), other.rational_value()
        match first, second:
            case Fraction(), Fraction():
                return ExactLocalValue.rational(self.place, first * second)
            case _:
                return ExactLocalValue(self.place, _ExactExpression("multiply", (self, other)))

    def valuation(self) -> int | float | None:
        """The exact p-adic valuation when determined by the retained expression."""
        assert isinstance(self.place, int)
        rational = self.rational_value()
        match rational:
            case Fraction() if rational == 0:
                return inf
            case Fraction():
                numerator, denominator = abs(rational.numerator), rational.denominator
                value = 0
                while numerator % self.place == 0:
                    numerator //= self.place
                    value += 1
                while denominator % self.place == 0:
                    denominator //= self.place
                    value -= 1
                return value
            case None:
                pass
        match self.expression.operation:
            case "atom":
                return cast(int | None, self.expression.arguments[1])
            case "negate":
                return cast(ExactLocalValue, self.expression.arguments[0]).valuation()
            case "multiply":
                first = cast(ExactLocalValue, self.expression.arguments[0]).valuation()
                second = cast(ExactLocalValue, self.expression.arguments[1]).valuation()
                return None if first is None or second is None else first + second
            case "add":
                first = cast(ExactLocalValue, self.expression.arguments[0]).valuation()
                second = cast(ExactLocalValue, self.expression.arguments[1]).valuation()
                match first, second:
                    case (None, _) | (_, None):
                        return None
                    case _ if first != second:
                        return min(first, second)
                    case _:
                        return None
            case _:
                return None

    def is_integral(self) -> bool | None:
        valuation = self.valuation()
        return None if valuation is None else valuation >= 0


@dataclass(frozen=True, eq=False, slots=True)
class ExactLocalFieldPresentation:
    """One exact field carrier and, for p-adic places, its certified valuation subring."""

    place: str | int
    ring: CategoryOfCategories.ElementType
    integers: CategoryOfCategories.ElementType | None

    def value(self, datum: Fraction | int) -> CategoryOfCategories.ElementType:
        carrier = Rings(Sets).forgetful().on_object(self.ring)
        return cast(
            CategoryOfCategories.ElementType,
            cast(Any, carrier).point(ExactLocalValue.rational(self.place, datum)),
        )

    def embed_rational(self, rational_ring: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        rings = Rings(Sets)
        source_carrier = rings.forgetful().on_object(rational_ring)
        target_carrier = rings.forgetful().on_object(self.ring)
        from sage_categories.cat.morphisms import Mor

        carrier_map = Mor(Sets)(source_carrier, target_carrier)(
            lambda value: ExactLocalValue.rational(self.place, cast(ExactLocalValue, value).rational_value() or Fraction(0))
        )
        return rings.homomorphism(rational_ring, self.ring, carrier_map)


def _exact_field(place: str | int) -> ExactLocalFieldPresentation:
    carrier = Sets.from_membership(lambda value: true if isinstance(value, ExactLocalValue) and value.place == place else false)
    zero = ExactLocalValue.rational(place, 0)
    one = ExactLocalValue.rational(place, 1)
    ring = certified_commutative_ring(
        carrier,
        lambda pair: cast(ExactLocalValue, pair[0]) + cast(ExactLocalValue, pair[1]),
        lambda pair: cast(ExactLocalValue, pair[0]) * cast(ExactLocalValue, pair[1]),
        zero,
        one,
    )
    integers = None
    match place:
        case int():
            integers = Sets.from_membership(lambda value: true if isinstance(value, ExactLocalValue) and value.place == place and value.is_integral() is True else false)
        case _:
            pass
    return ExactLocalFieldPresentation(place, ring, integers)


@cache
def exact_rational_field() -> ExactLocalFieldPresentation:
    return _exact_field("rational")


@cache
def exact_real_field() -> ExactLocalFieldPresentation:
    return _exact_field("real")


@cache
def exact_padic_field(prime: int) -> ExactLocalFieldPresentation:
    assert isprime(prime)
    return _exact_field(prime)


@cache
def prime_indices() -> CategoryOfCategories.ElementType:
    """The infinite set of positive prime integers, represented by its primality predicate."""
    return Sets.from_membership(lambda value: true if isinstance(value, int) and isprime(value) else false)
