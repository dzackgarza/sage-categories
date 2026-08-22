"""Cardinal numbers and their thin category.

The symbolic representation follows the cardinal-expression design in
``dzack_research.preamble.categories.sets.cardinals``. It uses no Sage
category or Sage parent.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any, TypeIs

from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    MathematicalObject,
    registered_value,
)


class Unknown(Enum):
    """The result of a mathematical question with no represented answer."""

    VALUE = "Unknown"

    def __bool__(self) -> bool:
        assert False, "Unknown is not a Boolean value"

    def __repr__(self) -> str:
        return "Unknown"


UNKNOWN = Unknown.VALUE
type Decision = bool | Unknown


class CardinalKind(Enum):
    FINITE = "finite"
    ALEPH = "aleph"
    SYMBOL = "symbol"
    UNKNOWN = "unknown"
    SUM = "sum"
    PRODUCT = "product"
    POWER = "power"
    INDEXED_SUM = "indexed sum"
    INDEXED_PRODUCT = "indexed product"


type CardinalFamily = Callable[[MathematicalObject], Cardinal]


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
        index_set: MathematicalObject | None = None,
        family: CardinalFamily | None = None,
    ) -> None:
        if kind is CardinalKind.FINITE:
            assert finite_value is not None and finite_value >= 0
        if kind is CardinalKind.ALEPH or kind is CardinalKind.SYMBOL:
            assert name is not None
        if kind is CardinalKind.POWER:
            assert len(terms) == 2
        if kind is CardinalKind.SUM or kind is CardinalKind.PRODUCT:
            assert terms
        if kind is CardinalKind.INDEXED_SUM or kind is CardinalKind.INDEXED_PRODUCT:
            assert index_set is not None and family is not None
        self._kind = kind
        self._finite_value = finite_value
        self._name = name
        self._terms = terms
        self._index_set = index_set
        self._family = family
        super().__init__(category=category)

    def kind(self) -> CardinalKind:
        return self._kind

    def finite_value(self) -> int:
        assert self._kind is CardinalKind.FINITE
        assert self._finite_value is not None
        return self._finite_value

    def terms(self) -> tuple[Cardinal, ...]:
        return self._terms

    def index_set(self) -> MathematicalObject:
        assert self._index_set is not None
        return self._index_set

    def family(self) -> CardinalFamily:
        assert self._family is not None
        return self._family

    def is_finite(self) -> Decision:
        if self._kind is CardinalKind.FINITE:
            return True
        if self._kind is CardinalKind.ALEPH:
            return False
        return UNKNOWN

    def is_infinite(self) -> Decision:
        finite = self.is_finite()
        if finite is UNKNOWN:
            return UNKNOWN
        return not finite

    def __int__(self) -> int:
        return self.finite_value()

    def __eq__(self, other: Any) -> bool:
        if other is self:
            return True
        if self._kind is CardinalKind.FINITE and self._finite_value == other:
            return True
        value = registered_value(other)
        if value is None or not Cardinals().contains_cardinal(value):
            return False
        if self._kind is CardinalKind.INDEXED_SUM or self._kind is CardinalKind.INDEXED_PRODUCT:
            return False
        return self._kind is value._kind and self._finite_value == value._finite_value and self._name == value._name and self._terms == value._terms

    def __hash__(self) -> int:
        if self._kind is CardinalKind.INDEXED_SUM or self._kind is CardinalKind.INDEXED_PRODUCT:
            return id(self)
        return hash((self._kind, self._finite_value, self._name, self._terms))

    def __add__(self, other: Cardinal) -> Cardinal:
        return Cardinals().sum(self, other)

    def __mul__(self, other: Cardinal) -> Cardinal:
        return Cardinals().product(self, other)

    def __pow__(self, exponent: Cardinal) -> Cardinal:
        return Cardinals().power(self, exponent)

    def __repr__(self) -> str:
        if self._kind is CardinalKind.FINITE:
            return str(self.finite_value())
        if self._kind is CardinalKind.ALEPH or self._kind is CardinalKind.SYMBOL:
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
        return f"{self._kind.value} over {self.index_set()}"


class CardinalMorphism(Arrow):
    """The unique represented arrow between comparable cardinals."""


class CardinalHomCategory(HomCategory):
    """A singleton hom category when its source is at most its target."""

    ObjectType = CardinalMorphism
    ElementType = CardinalMorphism

    def __call__(self) -> CardinalMorphism:
        source = self.domain()
        target = self.codomain()
        assert Cardinals().contains_cardinal(source)
        assert Cardinals().contains_cardinal(target)
        assert Cardinals().le(source, target) is True
        return self.ObjectType(hom_category=self)

    def identity(self, value: MathematicalObject | None = None) -> CardinalMorphism:
        assert value is None
        assert self.domain() is self.codomain()
        return self()

    def compose(self, second: Arrow, first: Arrow) -> CardinalMorphism:
        assert first in self.base_category().ArrowCategory()
        assert second in self.base_category().ArrowCategory()
        assert first.codomain() is second.domain()
        return self()


class CardinalsCategory(Category):
    """The thin category of represented cardinal numbers and inequalities."""

    ObjectType = Cardinal

    def __init__(self) -> None:
        self._finite_cardinals: dict[int, Cardinal] = {}
        self._named_cardinals: dict[tuple[CardinalKind, str], Cardinal] = {}
        self._unknown_cardinal: Cardinal | None = None
        super().__init__(object_type=Cardinal)

    def _hom_category_type(self) -> type[HomCategory]:
        return CardinalHomCategory

    def _hom_category_family_type(self) -> type[HomCategoryFamily]:
        return HomCategoryFamily

    def __call__(self, number: int) -> Cardinal:
        assert number >= 0
        cached = self._finite_cardinals.get(number)
        if cached is None:
            cached = Cardinal(
                category=self,
                kind=CardinalKind.FINITE,
                finite_value=number,
            )
            self._finite_cardinals[number] = cached
        return cached

    def aleph(self, name: str = "aleph_0") -> Cardinal:
        return self._named(CardinalKind.ALEPH, name)

    def symbol(self, name: str) -> Cardinal:
        return self._named(CardinalKind.SYMBOL, name)

    def _named(self, kind: CardinalKind, name: str) -> Cardinal:
        key = kind, name
        cached = self._named_cardinals.get(key)
        if cached is None:
            cached = Cardinal(category=self, kind=kind, name=name)
            self._named_cardinals[key] = cached
        return cached

    def unknown(self) -> Cardinal:
        if self._unknown_cardinal is None:
            self._unknown_cardinal = Cardinal(
                category=self,
                kind=CardinalKind.UNKNOWN,
            )
        return self._unknown_cardinal

    def contains_cardinal(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[Cardinal]:
        return candidate in self

    def sum(self, *summands: Cardinal) -> Cardinal:
        terms: list[Cardinal] = []
        finite_total = 0
        for summand in summands:
            if summand.kind() is CardinalKind.FINITE:
                finite_total += summand.finite_value()
            elif summand.kind() is CardinalKind.SUM:
                terms.extend(summand.terms())
            else:
                terms.append(summand)
        if not terms:
            return self(finite_total)
        if finite_total:
            terms.append(self(finite_total))
        if len(terms) == 1:
            return terms[0]
        return Cardinal(
            category=self,
            kind=CardinalKind.SUM,
            terms=tuple(terms),
        )

    def product(self, *factors: Cardinal) -> Cardinal:
        terms: list[Cardinal] = []
        finite_product = 1
        for factor in factors:
            if factor == 0:
                return self(0)
            if factor.kind() is CardinalKind.FINITE:
                finite_product *= factor.finite_value()
            elif factor.kind() is CardinalKind.PRODUCT:
                terms.extend(factor.terms())
            else:
                terms.append(factor)
        if not terms:
            return self(finite_product)
        if finite_product != 1:
            terms.append(self(finite_product))
        if len(terms) == 1:
            return terms[0]
        return Cardinal(
            category=self,
            kind=CardinalKind.PRODUCT,
            terms=tuple(terms),
        )

    def power(self, base: Cardinal, exponent: Cardinal) -> Cardinal:
        if exponent == 0:
            return self(1)
        if base == 0:
            return self(0)
        if base == 1:
            return self(1)
        if base.kind() is CardinalKind.FINITE and exponent.kind() is CardinalKind.FINITE:
            return self(base.finite_value() ** exponent.finite_value())
        return Cardinal(
            category=self,
            kind=CardinalKind.POWER,
            terms=(base, exponent),
        )

    def indexed_sum(
        self,
        index_set: MathematicalObject,
        summands: CardinalFamily,
    ) -> Cardinal:
        return Cardinal(
            category=self,
            kind=CardinalKind.INDEXED_SUM,
            index_set=index_set,
            family=summands,
        )

    def indexed_product(
        self,
        index_set: MathematicalObject,
        factors: CardinalFamily,
    ) -> Cardinal:
        return Cardinal(
            category=self,
            kind=CardinalKind.INDEXED_PRODUCT,
            index_set=index_set,
            family=factors,
        )

    def le(self, source: Cardinal, target: Cardinal) -> Decision:
        if source == target:
            return True
        if source.kind() is CardinalKind.FINITE and target.kind() is CardinalKind.FINITE:
            return source.finite_value() <= target.finite_value()
        if source.kind() is CardinalKind.FINITE and target.kind() is CardinalKind.ALEPH:
            return True
        if source.kind() is CardinalKind.ALEPH and target.kind() is CardinalKind.FINITE:
            return False
        return UNKNOWN

    def __repr__(self) -> str:
        return "Card"


_CARDINALS = CardinalsCategory()


def Cardinals() -> CardinalsCategory:
    return _CARDINALS


def is_cardinal(value: int | Cardinal) -> TypeIs[Cardinal]:
    represented = registered_value(value)
    return represented is not None and Cardinals().contains_cardinal(represented)


def cardinal(value: int | Cardinal) -> Cardinal:
    if is_cardinal(value):
        return value
    return Cardinals()(value)


def Aleph0() -> Cardinal:
    return Cardinals().aleph()


def SymbolicCardinal(name: str) -> Cardinal:
    return Cardinals().symbol(name)


def UnknownCardinality() -> Cardinal:
    return Cardinals().unknown()
