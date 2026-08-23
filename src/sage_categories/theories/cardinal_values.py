"""Cardinal numbers and their thin category.

The symbolic representation follows the cardinal-expression design in
``dzack_research.preamble.categories.sets.cardinals``. It uses no Sage
category or Sage parent.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING

from sage_categories.values import (
    UNKNOWN,
    Decision,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.cardinal_categories import CardinalsCategory
    from sage_categories.theories.ordinals import Ordinal
    from sage_categories.theories.sets import SetElement, SetObject


def _decision_and(left: Decision, right: Decision) -> Decision:
    if left is False or right is False:
        return False
    if left is UNKNOWN or right is UNKNOWN:
        return UNKNOWN
    return True


class CardinalKind(Enum):
    FINITE = "finite"
    ALEPH = "aleph"
    SYMBOL = "symbol"
    UNKNOWN = "unknown"
    SUM = "sum"
    PRODUCT = "product"
    POWER = "power"
    SUPREMUM = "supremum"
    INDEXED_SUM = "indexed sum"
    INDEXED_PRODUCT = "indexed product"


type CardinalFamily = Callable[[SetElement], Cardinal]


class Cardinal(MathematicalObject):
    """A finite, infinite, symbolic, or unknown cardinal number."""

    def __init__(
        self,
        *,
        category: CardinalsCategory,
        kind: CardinalKind,
        finite_value: int | None = None,
        name: str | None = None,
        terms: tuple[Cardinal, ...] = (),
        index: Ordinal | None = None,
        index_set: SetObject | None = None,
        family: CardinalFamily | None = None,
        finiteness: Decision = UNKNOWN,
    ) -> None:
        if kind is CardinalKind.FINITE:
            assert finite_value is not None and finite_value >= 0
        if kind is CardinalKind.ALEPH:
            assert index is not None
        if kind is CardinalKind.SYMBOL:
            assert name is not None
        if kind is CardinalKind.POWER:
            assert len(terms) == 2
        if kind is CardinalKind.SUM or kind is CardinalKind.PRODUCT or kind is CardinalKind.SUPREMUM:
            assert terms
        if kind is CardinalKind.INDEXED_SUM or kind is CardinalKind.INDEXED_PRODUCT:
            assert index_set is not None and family is not None
        self._kind = kind
        self._finite_value = finite_value
        self._name = name
        self._terms = terms
        self._index = index
        self._index_set = index_set
        self._family = family
        self._finiteness = finiteness
        super().__init__(category=category)

    def kind(self) -> CardinalKind:
        return self._kind

    def finite_value(self) -> int:
        assert self._kind is CardinalKind.FINITE
        assert self._finite_value is not None
        return self._finite_value

    def terms(self) -> tuple[Cardinal, ...]:
        return self._terms

    def index_set(self) -> SetObject:
        assert self._index_set is not None
        return self._index_set

    def family(self) -> CardinalFamily:
        assert self._family is not None
        return self._family

    def is_aleph(self) -> bool:
        return self._kind is CardinalKind.ALEPH

    def is_continuum(self) -> bool:
        return self._kind is CardinalKind.POWER and self._terms[0] == 2 and self._terms[1].is_countably_infinite()

    def is_countably_infinite(self) -> bool:
        return self._kind is CardinalKind.ALEPH and self.aleph_index() == 0

    def aleph_index(self) -> Ordinal:
        assert self._kind is CardinalKind.ALEPH
        assert self._index is not None
        return self._index

    def initial_ordinal(self) -> Ordinal:
        from sage_categories.theories.ordinals import omega, ordinal

        if self._kind is CardinalKind.FINITE:
            return ordinal(self.finite_value())
        assert self._kind is CardinalKind.ALEPH
        return omega(self.aleph_index())

    def cardinality(self) -> Cardinal:
        return self

    def sort_key(self) -> tuple[int, str]:
        if self._kind is CardinalKind.FINITE:
            return 0, repr(self)
        if self._kind is CardinalKind.ALEPH:
            return 1, repr(self)
        if self._kind is CardinalKind.POWER:
            return 2, repr(self)
        if self._kind is CardinalKind.SUPREMUM:
            return 3, repr(self)
        return 4, repr(self)

    def is_finite(self) -> Decision:
        if self._finiteness is not UNKNOWN:
            return self._finiteness
        if self._kind is CardinalKind.FINITE:
            return True
        if self._kind is CardinalKind.ALEPH:
            return False
        if self._kind is CardinalKind.SUPREMUM:
            answers = tuple(term.is_finite() for term in self._terms)
            if all(answer is True for answer in answers):
                return True
            if any(answer is False for answer in answers):
                return False
        return UNKNOWN

    def is_infinite(self) -> Decision:
        if self._finiteness is not UNKNOWN:
            return not self._finiteness
        if self._kind is CardinalKind.FINITE:
            return False
        if self._kind is CardinalKind.ALEPH or self.is_continuum():
            return True
        if self._kind is CardinalKind.SUPREMUM:
            answers = tuple(term.is_infinite() for term in self._terms)
            if any(answer is True for answer in answers):
                return True
            if all(answer is False for answer in answers):
                return False
        return UNKNOWN

    def is_countable(self) -> Decision:
        if self._finiteness is True:
            return True
        if self._kind is CardinalKind.FINITE:
            return True
        if self._kind is CardinalKind.ALEPH:
            return self.is_countably_infinite()
        if self._kind is CardinalKind.SUPREMUM:
            answers = tuple(term.is_countable() for term in self._terms)
            if all(answer is True for answer in answers):
                return True
            if any(answer is False for answer in answers):
                return False
        if self.is_continuum():
            return False
        return UNKNOWN

    def is_uncountable(self) -> Decision:
        countable = self.is_countable()
        if countable is UNKNOWN:
            return UNKNOWN
        return not countable

    def is_uncountably_infinite(self) -> Decision:
        return _decision_and(self.is_infinite(), self.is_uncountable())

    def __int__(self) -> int:
        return self.finite_value()

    def __index__(self) -> int:
        return self.finite_value()

    def __eq__(self, candidate: object) -> bool:
        if candidate is self:
            return True
        if self._kind is CardinalKind.FINITE and self._finite_value == candidate:
            return True
        value = registered_value(candidate)
        if value is None or not _cardinals().contains_cardinal(value):
            return False
        if self._kind is CardinalKind.INDEXED_SUM or self._kind is CardinalKind.INDEXED_PRODUCT:
            return False
        return (
            self._kind is value._kind
            and self._finite_value == value._finite_value
            and self._name == value._name
            and self._terms == value._terms
            and self._index == value._index
        )

    def __hash__(self) -> int:
        if self._kind is CardinalKind.FINITE:
            return hash(self.finite_value())
        if self._kind is CardinalKind.INDEXED_SUM or self._kind is CardinalKind.INDEXED_PRODUCT:
            return id(self)
        return hash(
            (
                self._kind,
                self._finite_value,
                self._name,
                self._terms,
                self._index,
            )
        )

    def __le__(self, other: Cardinal | int) -> Decision:
        return _cardinals()._is_lequal(self, _cardinal(other))

    def __lt__(self, other: Cardinal | int) -> Decision:
        return _cardinals()._is_less_than(self, _cardinal(other))

    def __ge__(self, other: Cardinal | int) -> Decision:
        return _cardinals()._is_lequal(_cardinal(other), self)

    def __gt__(self, other: Cardinal | int) -> Decision:
        return _cardinals()._is_less_than(_cardinal(other), self)

    def __add__(self, other: Cardinal) -> Cardinal:
        return _cardinals().sum(self, other)

    def __radd__(self, other: Cardinal | int) -> Cardinal:
        return _cardinals().sum(_cardinal(other), self)

    def __mul__(self, other: Cardinal) -> Cardinal:
        return _cardinals().product(self, other)

    def __rmul__(self, other: Cardinal | int) -> Cardinal:
        return _cardinals().product(_cardinal(other), self)

    def __pow__(self, exponent: Cardinal) -> Cardinal:
        return _cardinals().power(self, exponent)

    def __rpow__(self, base: Cardinal | int) -> Cardinal:
        return _cardinals().power(_cardinal(base), self)

    def __repr__(self) -> str:
        if self._kind is CardinalKind.FINITE:
            return str(self.finite_value())
        if self._kind is CardinalKind.ALEPH:
            return f"ℵ_{self.aleph_index()}"
        if self._kind is CardinalKind.SYMBOL:
            assert self._name is not None
            return self._name
        if self._kind is CardinalKind.UNKNOWN:
            return "Unknown cardinality"
        if self._kind is CardinalKind.SUM:
            return " + ".join(map(str, self._terms))
        if self._kind is CardinalKind.PRODUCT:
            return " * ".join(map(str, self._terms))
        if self._kind is CardinalKind.POWER:
            return f"({self._terms[0]})^({self._terms[1]})"
        if self._kind is CardinalKind.SUPREMUM:
            return "sup(" + ", ".join(map(str, self._terms)) + ")"
        return f"{self._kind.value} over {self.index_set()}"


def _cardinals() -> CardinalsCategory:
    from sage_categories.theories.cardinal_categories import Cardinals

    return Cardinals()


def _cardinal(value: int | Cardinal) -> Cardinal:
    from sage_categories.theories.cardinals import cardinal

    return cardinal(value)
