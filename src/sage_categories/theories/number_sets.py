"""The standard number sets as owned objects of ``Sets()``.

Only their set structure belongs to the current foundational phase.  Integer
and rational representatives use Python's integer and ``fractions.Fraction``
implementations.  These are established canonical representations, while the
public values remain owned set elements.
"""

from __future__ import annotations

from collections.abc import Iterator
from fractions import Fraction
from typing import TypeIs

from sage_categories.theories.cardinals import aleph0, continuum
from sage_categories.theories.sets import (
    SetElement,
    SetElements,
    SetObject,
    Sets,
)
from sage_categories.values import Decision, MathematicalObject


class IntegerElement(SetElement):
    """An integer as an element of the owned integer set."""

    def __init__(self, ambient_set: IntegerSet, integer: int) -> None:
        self._integer = integer
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_set,
        )

    def __int__(self) -> int:
        return self._integer

    def __index__(self) -> int:
        return self._integer

    def is_prime(self) -> bool:
        """Return whether this integer is prime."""
        from sage.rings.integer import Integer as SageIntegerValue

        return bool(SageIntegerValue(self._integer).is_prime())

    def __repr__(self) -> str:
        return str(self._integer)


class IntegerSet(SetObject):
    """The set of integers."""

    def __init__(self) -> None:
        from sage_categories.theories.sets import Sets

        self._integers: dict[int, IntegerElement] = {}
        super().__init__(category=Sets(), cardinality=aleph0)

    def __call__(self, integer: int | IntegerElement) -> IntegerElement:
        value = int(integer)
        cached = self._integers.get(value)
        if cached is None:
            cached = IntegerElement(self, value)
            self._integers[value] = cached
        return cached

    def _membership_(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def contains_integer(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[IntegerElement]:
        return candidate in self

    def _set_iterator_(self) -> Iterator[SetElement]:
        yield self(0)
        magnitude = 1
        while True:
            yield self(magnitude)
            yield self(-magnitude)
            magnitude += 1

    def __repr__(self) -> str:
        return "Integers"


_INTEGERS: MathematicalObject | None = None


def Integers() -> MathematicalObject:
    global _INTEGERS

    if _INTEGERS is None:
        from sage_categories.theories.sets import CountableSets

        _INTEGERS = CountableSets()(IntegerSet())
    return _INTEGERS


class RationalElement(SetElement):
    """A rational number as an element of the owned rational set."""

    def __init__(self, ambient_set: RationalSet, rational: Fraction) -> None:
        self._rational = rational
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_set,
        )

    def numerator(self) -> IntegerElement:
        return Integers()(self._rational.numerator)

    def denominator(self) -> IntegerElement:
        return Integers()(self._rational.denominator)

    def floor(self) -> IntegerElement:
        return Integers()(
            self._rational.numerator // self._rational.denominator,
        )

    def __repr__(self) -> str:
        return repr(self._rational)


class RationalSet(SetObject):
    """The set of rational numbers."""

    def __init__(self) -> None:
        from sage_categories.theories.sets import Sets

        self._rationals: dict[Fraction, RationalElement] = {}
        super().__init__(category=Sets(), cardinality=aleph0)

    def __call__(
        self,
        numerator: int | IntegerElement,
        denominator: int | IntegerElement = 1,
    ) -> RationalElement:
        rational = Fraction(int(numerator), int(denominator))
        cached = self._rationals.get(rational)
        if cached is None:
            cached = RationalElement(self, rational)
            self._rationals[rational] = cached
        return cached

    def _membership_(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def contains_rational(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[RationalElement]:
        return candidate in self

    def __repr__(self) -> str:
        return "Rational numbers"


_RATIONALS: MathematicalObject | None = None


def Rationals() -> MathematicalObject:
    global _RATIONALS

    if _RATIONALS is None:
        from sage_categories.theories.sets import CountableSets

        _RATIONALS = CountableSets()(RationalSet())
    return _RATIONALS


class RealElement(SetElement):
    """A represented real number in the owned real set."""

    def __init__(self, ambient_set: RealSet, rational: RationalElement) -> None:
        self._rational = rational
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_set,
        )

    def rational(self) -> RationalElement:
        return self._rational

    def __repr__(self) -> str:
        return repr(self._rational)


class RealSet(SetObject):
    """The set of real numbers with exact rational representatives available."""

    def __init__(self) -> None:
        from sage_categories.theories.sets import Sets

        self._rationals: dict[RationalElement, RealElement] = {}
        super().__init__(category=Sets(), cardinality=continuum)

    def __call__(self, integer: int | IntegerElement) -> RealElement:
        return self.rational(Rationals()(integer))

    def rational(self, rational: RationalElement) -> RealElement:
        assert rational.ambient_set() is Rationals()
        cached = self._rationals.get(rational)
        if cached is None:
            cached = RealElement(self, rational)
            self._rationals[rational] = cached
        return cached

    def _membership_(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def contains_real(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[RealElement]:
        return candidate in self

    def __repr__(self) -> str:
        return "Real numbers"


_REAL_NUMBERS: MathematicalObject | None = None


def RealNumbers() -> MathematicalObject:
    global _REAL_NUMBERS

    if _REAL_NUMBERS is None:
        from sage_categories.theories.sets import UncountableSets

        _REAL_NUMBERS = UncountableSets()(RealSet())
    return _REAL_NUMBERS


ZZ = Integers()
QQ = Rationals()
RR = RealNumbers()
