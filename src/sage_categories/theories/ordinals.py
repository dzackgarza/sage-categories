"""Ordinals and their natural semiring operations.

This expression model migrates
``dzack_research.preamble.categories.sets.ordinals``. Its arithmetic follows
Mathlib's ``SetTheory/Ordinal/Arithmetic.lean`` implementation.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.hom_categories import HomCategory
from sage_categories.category import Category
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.cardinals import Cardinal


class OrdinalKind(Enum):
    FINITE = "finite"
    INITIAL = "initial"
    NATURAL_SUM = "natural sum"
    NATURAL_PRODUCT = "natural product"
    ORDINAL_SUM = "ordinal sum"
    ORDINAL_PRODUCT = "ordinal product"
    ORDINAL_POWER = "ordinal power"


type OrdinalInput = int | Ordinal


class Ordinal(MathematicalObject):
    """An ordinal represented by a canonical expression."""

    def __init__(
        self,
        *,
        category: OrdinalsCategory,
        kind: OrdinalKind,
        finite_value: int | None = None,
        terms: tuple[Ordinal, ...] = (),
        index: Ordinal | None = None,
    ) -> None:
        if kind is OrdinalKind.FINITE:
            assert finite_value is not None and finite_value >= 0
        if kind is OrdinalKind.INITIAL:
            assert index is not None
        if kind is OrdinalKind.NATURAL_SUM or kind is OrdinalKind.NATURAL_PRODUCT:
            assert terms
        if kind is OrdinalKind.ORDINAL_SUM or kind is OrdinalKind.ORDINAL_PRODUCT or kind is OrdinalKind.ORDINAL_POWER:
            assert len(terms) == 2
        self._kind = kind
        self._finite_value = finite_value
        self._terms = terms
        self._index = index
        super().__init__(category=category)

    def kind(self) -> OrdinalKind:
        return self._kind

    def finite_value(self) -> int:
        assert self._kind is OrdinalKind.FINITE
        assert self._finite_value is not None
        return self._finite_value

    def terms(self) -> tuple[Ordinal, ...]:
        return self._terms

    def is_initial(self) -> bool:
        return self._kind is OrdinalKind.INITIAL

    def initial_index(self) -> Ordinal:
        assert self._kind is OrdinalKind.INITIAL
        assert self._index is not None
        return self._index

    def cardinality(self) -> Cardinal:
        from sage_categories.theories.cardinals import Cardinals, aleph, cardinal

        if self._kind is OrdinalKind.FINITE:
            return cardinal(self.finite_value())
        if self._kind is OrdinalKind.INITIAL:
            return aleph(self.initial_index())
        if self._kind is OrdinalKind.NATURAL_SUM or self._kind is OrdinalKind.ORDINAL_SUM:
            return Cardinals().sum(*(term.cardinality() for term in self._terms))
        if self._kind is OrdinalKind.NATURAL_PRODUCT or self._kind is OrdinalKind.ORDINAL_PRODUCT:
            return Cardinals().product(*(term.cardinality() for term in self._terms))
        return Cardinals().power(
            self._terms[0].cardinality(),
            self._terms[1].cardinality(),
        )

    def __eq__(self, other: Any) -> bool:
        if other is self:
            return True
        if self._kind is OrdinalKind.FINITE and self._finite_value == other:
            return True
        value = registered_value(other)
        if value is None or not Ordinals().contains_ordinal(value):
            return False
        return self._kind is value._kind and self._finite_value == value._finite_value and self._terms == value._terms and self._index == value._index

    def __hash__(self) -> int:
        if self._kind is OrdinalKind.FINITE:
            return hash(self.finite_value())
        return hash((self._kind, self._finite_value, self._terms, self._index))

    def __int__(self) -> int:
        return self.finite_value()

    def __index__(self) -> int:
        return self.finite_value()

    def __le__(self, other: OrdinalInput) -> Decision:
        return Ordinals().le(self, ordinal(other))

    def __lt__(self, other: OrdinalInput) -> Decision:
        return Ordinals().lt(self, ordinal(other))

    def __ge__(self, other: OrdinalInput) -> Decision:
        return Ordinals().le(ordinal(other), self)

    def __gt__(self, other: OrdinalInput) -> Decision:
        return Ordinals().lt(ordinal(other), self)

    def __add__(self, other: OrdinalInput) -> Ordinal:
        return Ordinals().natural_sum(self, ordinal(other))

    def __radd__(self, other: OrdinalInput) -> Ordinal:
        return Ordinals().natural_sum(ordinal(other), self)

    def __mul__(self, other: OrdinalInput) -> Ordinal:
        return Ordinals().natural_product(self, ordinal(other))

    def __rmul__(self, other: OrdinalInput) -> Ordinal:
        return Ordinals().natural_product(ordinal(other), self)

    def ordinal_sum(self, other: OrdinalInput) -> Ordinal:
        return Ordinals().ordinal_sum(self, ordinal(other))

    def ordinal_product(self, other: OrdinalInput) -> Ordinal:
        return Ordinals().ordinal_product(self, ordinal(other))

    def ordinal_power(self, exponent: OrdinalInput) -> Ordinal:
        return Ordinals().ordinal_power(self, ordinal(exponent))

    def __repr__(self) -> str:
        if self._kind is OrdinalKind.FINITE:
            return str(self.finite_value())
        if self._kind is OrdinalKind.INITIAL:
            return f"ω_{self.initial_index()}"
        if self._kind is OrdinalKind.NATURAL_SUM:
            return " # ".join(map(str, self._terms))
        if self._kind is OrdinalKind.NATURAL_PRODUCT:
            return " ⊗ ".join(map(str, self._terms))
        if self._kind is OrdinalKind.ORDINAL_SUM:
            return f"({self._terms[0]} +o {self._terms[1]})"
        if self._kind is OrdinalKind.ORDINAL_PRODUCT:
            return f"({self._terms[0]} *o {self._terms[1]})"
        return f"({self._terms[0]} ^o {self._terms[1]})"


class OrdinalMorphism(Arrow):
    """The unique represented arrow between comparable ordinals."""


class OrdinalHomCategory(HomCategory):
    ObjectType = OrdinalMorphism
    ElementType = OrdinalMorphism

    def __call__(self) -> OrdinalMorphism:
        source = self.domain()
        target = self.codomain()
        assert Ordinals().contains_ordinal(source)
        assert Ordinals().contains_ordinal(target)
        assert Ordinals().le(source, target) is True
        return self.ObjectType(hom_category=self)

    def identity(self, value: MathematicalObject | None = None) -> OrdinalMorphism:
        assert value is None
        assert self.domain() is self.codomain()
        return self()

    def compose(self, second: Arrow, first: Arrow) -> OrdinalMorphism:
        assert first in self.base_category().ArrowCategory()
        assert second in self.base_category().ArrowCategory()
        assert first.codomain() is second.domain()
        return self()


class OrdinalsCategory(Category):
    """The thin category of ordinals under their represented order."""

    ObjectType = Ordinal

    def __init__(self) -> None:
        self._finite_ordinals: dict[int, Ordinal] = {}
        self._initial_ordinals: dict[Ordinal, Ordinal] = {}
        self._expressions: dict[
            tuple[OrdinalKind, tuple[Ordinal, ...]],
            Ordinal,
        ] = {}
        super().__init__(object_type=Ordinal)

    def _hom_category_type(self) -> type[HomCategory]:
        return OrdinalHomCategory

    def __call__(self, number: int) -> Ordinal:
        assert number >= 0
        cached = self._finite_ordinals.get(number)
        if cached is None:
            cached = Ordinal(
                category=self,
                kind=OrdinalKind.FINITE,
                finite_value=number,
            )
            self._finite_ordinals[number] = cached
        return cached

    def contains_ordinal(self, candidate: MathematicalObject) -> TypeIs[Ordinal]:
        return candidate in self

    def zero(self) -> Ordinal:
        return self(0)

    def one(self) -> Ordinal:
        return self(1)

    def initial(self, index: OrdinalInput) -> Ordinal:
        ordinal_index = ordinal(index)
        cached = self._initial_ordinals.get(ordinal_index)
        if cached is None:
            cached = Ordinal(
                category=self,
                kind=OrdinalKind.INITIAL,
                index=ordinal_index,
            )
            self._initial_ordinals[ordinal_index] = cached
        return cached

    def natural_sum(self, *summands: Ordinal) -> Ordinal:
        terms: list[Ordinal] = []
        finite_part = 0
        for summand in summands:
            if summand.kind() is OrdinalKind.FINITE:
                finite_part += summand.finite_value()
            elif summand.kind() is OrdinalKind.NATURAL_SUM:
                terms.extend(summand.terms())
            else:
                terms.append(summand)
        if finite_part:
            terms.append(self(finite_part))
        if not terms:
            return self.zero()
        terms.sort(key=repr)
        if len(terms) == 1:
            return terms[0]
        return self._expression(OrdinalKind.NATURAL_SUM, tuple(terms))

    def natural_product(self, *factors: Ordinal) -> Ordinal:
        for index, factor in enumerate(factors):
            if factor.kind() is OrdinalKind.NATURAL_SUM:
                preceding = factors[:index]
                following = factors[index + 1 :]
                return self.natural_sum(*(self.natural_product(*preceding, term, *following) for term in factor.terms()))
        terms: list[Ordinal] = []
        finite_part = 1
        for factor in factors:
            if factor.kind() is OrdinalKind.FINITE:
                if factor == 0:
                    return self.zero()
                finite_part *= factor.finite_value()
            elif factor.kind() is OrdinalKind.NATURAL_PRODUCT:
                terms.extend(factor.terms())
            else:
                terms.append(factor)
        if finite_part != 1 or not terms:
            terms.append(self(finite_part))
        terms.sort(key=repr)
        if len(terms) == 1:
            return terms[0]
        return self._expression(OrdinalKind.NATURAL_PRODUCT, tuple(terms))

    def ordinal_sum(self, left: Ordinal, right: Ordinal) -> Ordinal:
        if left.kind() is OrdinalKind.FINITE and right.kind() is OrdinalKind.FINITE:
            return self(left.finite_value() + right.finite_value())
        if left == 0:
            return right
        if right == 0:
            return left
        return self._expression(OrdinalKind.ORDINAL_SUM, (left, right))

    def ordinal_product(self, left: Ordinal, right: Ordinal) -> Ordinal:
        if left.kind() is OrdinalKind.FINITE and right.kind() is OrdinalKind.FINITE:
            return self(left.finite_value() * right.finite_value())
        if left == 0 or right == 0:
            return self.zero()
        if left == 1:
            return right
        if right == 1:
            return left
        return self._expression(OrdinalKind.ORDINAL_PRODUCT, (left, right))

    def ordinal_power(self, base: Ordinal, exponent: Ordinal) -> Ordinal:
        if base.kind() is OrdinalKind.FINITE and exponent.kind() is OrdinalKind.FINITE:
            return self(base.finite_value() ** exponent.finite_value())
        if exponent == 0:
            return self.one()
        if base == 0:
            return self.zero()
        if base == 1:
            return self.one()
        return self._expression(OrdinalKind.ORDINAL_POWER, (base, exponent))

    def _expression(
        self,
        kind: OrdinalKind,
        terms: tuple[Ordinal, ...],
    ) -> Ordinal:
        key = kind, terms
        cached = self._expressions.get(key)
        if cached is None:
            cached = Ordinal(category=self, kind=kind, terms=terms)
            self._expressions[key] = cached
        return cached

    def le(self, source: Ordinal, target: Ordinal) -> Decision:
        if source == target:
            return True
        if source.kind() is OrdinalKind.FINITE:
            if target.kind() is OrdinalKind.FINITE:
                return source.finite_value() <= target.finite_value()
            return True
        if target.kind() is OrdinalKind.FINITE:
            return False
        if source.kind() is OrdinalKind.INITIAL and target.kind() is OrdinalKind.INITIAL:
            return self.le(source.initial_index(), target.initial_index())
        return UNKNOWN

    def lt(self, source: Ordinal, target: Ordinal) -> Decision:
        if source == target:
            return False
        return self.le(source, target)

    def __repr__(self) -> str:
        return "Ordinals"


_ORDINALS = OrdinalsCategory()


def Ordinals() -> OrdinalsCategory:
    return _ORDINALS


def is_ordinal(value: OrdinalInput) -> TypeIs[Ordinal]:
    represented = registered_value(value)
    return represented is not None and Ordinals().contains_ordinal(represented)


def ordinal(value: OrdinalInput) -> Ordinal:
    if is_ordinal(value):
        return value
    return Ordinals()(value)


def omega(index: OrdinalInput) -> Ordinal:
    return Ordinals().initial(index)


omega0 = omega(0)
