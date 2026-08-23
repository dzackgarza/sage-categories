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
from sage_categories.theories.sets import SetElement, SetElements, SetObject, Sets
from sage_categories.values import Decision, MathematicalObject


class IntegerElement(SetElement):
    """An integer as an element of the owned integer set."""

    def __init__(self, integer: int) -> None:
        self._integer = integer
        super().__init__(
            category=SetElements(),
            ambient_object=Integers(),
        )

    def __int__(self) -> int:
        return self._integer

    def __index__(self) -> int:
        return self._integer

    def __repr__(self) -> str:
        return str(self._integer)


class IntegerSet(SetObject):
    """The set of integers."""

    def __init__(self) -> None:
        self._integers: dict[int, IntegerElement] = {}
        super().__init__(category=Sets(), cardinality=aleph0)

    def __call__(self, integer: int | IntegerElement) -> IntegerElement:
        value = int(integer)
        cached = self._integers.get(value)
        if cached is None:
            cached = IntegerElement(value)
            self._integers[value] = cached
        return cached

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def contains_integer(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[IntegerElement]:
        return candidate in self

    def __iter__(self) -> Iterator[SetElement]:
        yield self(0)
        magnitude = 1
        while True:
            yield self(magnitude)
            yield self(-magnitude)
            magnitude += 1

    def __repr__(self) -> str:
        return "Integers"


_INTEGERS: IntegerSet | None = None


def Integers() -> IntegerSet:
    global _INTEGERS

    if _INTEGERS is None:
        _INTEGERS = IntegerSet()
    return _INTEGERS


class RationalElement(SetElement):
    """A rational number as an element of the owned rational set."""

    def __init__(self, rational: Fraction) -> None:
        self._rational = rational
        super().__init__(
            category=SetElements(),
            ambient_object=Rationals(),
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
            cached = RationalElement(rational)
            self._rationals[rational] = cached
        return cached

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def contains_rational(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[RationalElement]:
        return candidate in self

    def __repr__(self) -> str:
        return "Rational numbers"


_RATIONALS: RationalSet | None = None


def Rationals() -> RationalSet:
    global _RATIONALS

    if _RATIONALS is None:
        _RATIONALS = RationalSet()
    return _RATIONALS


class RealElement(SetElement):
    """A represented real number in the owned real set."""

    def __init__(self, rational: RationalElement) -> None:
        self._rational = rational
        super().__init__(
            category=SetElements(),
            ambient_object=RealNumbers(),
        )

    def rational(self) -> RationalElement:
        return self._rational

    def __repr__(self) -> str:
        return repr(self._rational)


class RealSet(SetObject):
    """The set of real numbers with exact rational representatives available."""

    def __init__(self) -> None:
        self._rationals: dict[RationalElement, RealElement] = {}
        super().__init__(category=Sets(), cardinality=continuum)

    def __call__(self, integer: int | IntegerElement) -> RealElement:
        return self.rational(Rationals()(integer))

    def rational(self, rational: RationalElement) -> RealElement:
        assert rational.ambient_set() is Rationals()
        cached = self._rationals.get(rational)
        if cached is None:
            cached = RealElement(rational)
            self._rationals[rational] = cached
        return cached

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def contains_real(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[RealElement]:
        return candidate in self

    def __repr__(self) -> str:
        return "Real numbers"


_REAL_NUMBERS: RealSet | None = None


def RealNumbers() -> RealSet:
    global _REAL_NUMBERS

    if _REAL_NUMBERS is None:
        _REAL_NUMBERS = RealSet()
    return _REAL_NUMBERS


ZZ = Integers()
QQ = Rationals()
RR = RealNumbers()
