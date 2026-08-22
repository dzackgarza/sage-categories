"""Cardinal numbers and their thin category.

The symbolic representation follows the cardinal-expression design in
``dzack_research.preamble.categories.sets.cardinals``. It uses no Sage
category or Sage parent.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, TypeIs

from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.category import Category
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalObject,
    Unknown,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.ordinals import Ordinal, OrdinalInput


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


type CardinalFamily = Callable[[MathematicalObject], Cardinal]


class CardinalComparison(Enum):
    LESS = -1
    EQUAL = 0
    GREATER = 1


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
        index_set: MathematicalObject | None = None,
        family: CardinalFamily | None = None,
    ) -> None:
        if kind is CardinalKind.FINITE:
            assert finite_value is not None and finite_value >= 0
        if kind is CardinalKind.ALEPH:
            assert index is not None
        if kind is CardinalKind.SYMBOL:
            assert name is not None
        if kind is CardinalKind.POWER:
            assert len(terms) == 2
        if (
            kind is CardinalKind.SUM
            or kind is CardinalKind.PRODUCT
            or kind is CardinalKind.SUPREMUM
        ):
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

    def is_aleph(self) -> bool:
        return self._kind is CardinalKind.ALEPH

    def is_continuum(self) -> bool:
        return (
            self._kind is CardinalKind.POWER
            and self._terms[0] == 2
            and self._terms[1].is_countably_infinite()
        )

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

    def __eq__(self, other: object) -> bool:
        if other is self:
            return True
        if self._kind is CardinalKind.FINITE and self._finite_value == other:
            return True
        value = registered_value(other)
        if value is None or not Cardinals().contains_cardinal(value):
            return False
        if (
            self._kind is CardinalKind.INDEXED_SUM
            or self._kind is CardinalKind.INDEXED_PRODUCT
        ):
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
        if (
            self._kind is CardinalKind.INDEXED_SUM
            or self._kind is CardinalKind.INDEXED_PRODUCT
        ):
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
        return Cardinals().le(self, cardinal(other))

    def __lt__(self, other: Cardinal | int) -> Decision:
        return Cardinals().lt(self, cardinal(other))

    def __ge__(self, other: Cardinal | int) -> Decision:
        return Cardinals().le(cardinal(other), self)

    def __gt__(self, other: Cardinal | int) -> Decision:
        return Cardinals().lt(cardinal(other), self)

    def __add__(self, other: Cardinal) -> Cardinal:
        return Cardinals().sum(self, other)

    def __radd__(self, other: Cardinal | int) -> Cardinal:
        return Cardinals().sum(cardinal(other), self)

    def __mul__(self, other: Cardinal) -> Cardinal:
        return Cardinals().product(self, other)

    def __rmul__(self, other: Cardinal | int) -> Cardinal:
        return Cardinals().product(cardinal(other), self)

    def __pow__(self, exponent: Cardinal) -> Cardinal:
        return Cardinals().power(self, exponent)

    def __rpow__(self, base: Cardinal | int) -> Cardinal:
        return Cardinals().power(cardinal(base), self)

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


class CardinalMorphism(Arrow):
    """The unique represented arrow between comparable cardinals."""

    def __repr__(self) -> str:
        return f"{self.domain()} <= {self.codomain()}"


class CardinalHomCategory(HomCategory):
    """A singleton hom category when its source is at most its target."""

    ObjectType = CardinalMorphism
    ElementType = CardinalMorphism

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: HomCategoryFamily,
    ) -> None:
        self._unique_morphism: CardinalMorphism | None = None
        super().__init__(
            domain=domain,
            codomain=codomain,
            hom_category=hom_category,
        )

    def unique_morphism(self) -> CardinalMorphism:
        source = self.domain()
        target = self.codomain()
        assert Cardinals().contains_cardinal(source)
        assert Cardinals().contains_cardinal(target)
        assert Cardinals().le(source, target) is True
        if self._unique_morphism is None:
            self._unique_morphism = self.ObjectType(hom_category=self)
        return self._unique_morphism

    def __call__(self) -> CardinalMorphism:
        return self.unique_morphism()

    def objects(self) -> MathematicalObject:
        from sage_categories.theories.sets import FiniteSet

        source = self.domain()
        target = self.codomain()
        assert Cardinals().contains_cardinal(source)
        assert Cardinals().contains_cardinal(target)
        members: frozenset[CardinalMorphism] = frozenset()
        if Cardinals().le(source, target) is True:
            members = frozenset({self.unique_morphism()})
        return FiniteSet(members)

    def identity(self, value: MathematicalObject | None = None) -> CardinalMorphism:
        assert value is None
        assert self.domain() == self.codomain()
        return self.unique_morphism()

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
        self._aleph_cardinals: dict[Ordinal, Cardinal] = {}
        self._symbolic_cardinals: dict[str, Cardinal] = {}
        self._unknown_cardinal: Cardinal | None = None
        super().__init__(object_type=Cardinal)

    def _hom_category_type(self) -> type[HomCategory]:
        return CardinalHomCategory

    def _hom_category_family_type(self) -> type[HomCategoryFamily]:
        return HomCategoryFamily

    def __call__(self, number: int) -> Cardinal:
        normalized = int(number)
        assert normalized == number
        assert normalized >= 0
        cached = self._finite_cardinals.get(normalized)
        if cached is None:
            cached = Cardinal(
                category=self,
                kind=CardinalKind.FINITE,
                finite_value=normalized,
            )
            self._finite_cardinals[normalized] = cached
        return cached

    def zero(self) -> Cardinal:
        return self(0)

    def one(self) -> Cardinal:
        return self(1)

    def aleph(self, index: OrdinalInput = 0) -> Cardinal:
        from sage_categories.theories.ordinals import ordinal

        ordinal_index = ordinal(index)
        cached = self._aleph_cardinals.get(ordinal_index)
        if cached is None:
            cached = Cardinal(
                category=self,
                kind=CardinalKind.ALEPH,
                index=ordinal_index,
            )
            self._aleph_cardinals[ordinal_index] = cached
        return cached

    def symbol(self, name: str) -> Cardinal:
        cached = self._symbolic_cardinals.get(name)
        if cached is None:
            cached = Cardinal(
                category=self,
                kind=CardinalKind.SYMBOL,
                name=name,
            )
            self._symbolic_cardinals[name] = cached
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
        infinite_terms: list[Cardinal] = []
        formal_terms: list[Cardinal] = []
        finite_total = 0
        for summand in summands:
            if summand.kind() is CardinalKind.FINITE:
                finite_total += summand.finite_value()
            elif summand.is_infinite() is True:
                infinite_terms.append(summand)
            elif summand.kind() is CardinalKind.SUM:
                formal_terms.extend(summand.terms())
            else:
                formal_terms.append(summand)
        if infinite_terms and not formal_terms:
            return self.supremum(*infinite_terms)
        if infinite_terms:
            formal_terms.extend(infinite_terms)
        if not formal_terms:
            return self(finite_total)
        if finite_total:
            formal_terms.append(self(finite_total))
        if len(formal_terms) == 1:
            return formal_terms[0]
        return Cardinal(
            category=self,
            kind=CardinalKind.SUM,
            terms=tuple(formal_terms),
        )

    def product(self, *factors: Cardinal) -> Cardinal:
        infinite_terms: list[Cardinal] = []
        formal_terms: list[Cardinal] = []
        finite_product = 1
        for factor in factors:
            if factor == 0:
                return self(0)
            if factor.kind() is CardinalKind.FINITE:
                finite_product *= factor.finite_value()
            elif factor.is_infinite() is True:
                infinite_terms.append(factor)
            elif factor.kind() is CardinalKind.PRODUCT:
                formal_terms.extend(factor.terms())
            else:
                formal_terms.append(factor)
        if infinite_terms and not formal_terms:
            return self.supremum(*infinite_terms)
        if infinite_terms:
            formal_terms.extend(infinite_terms)
        if not formal_terms:
            return self(finite_product)
        if finite_product != 1:
            formal_terms.append(self(finite_product))
        if len(formal_terms) == 1:
            return formal_terms[0]
        return Cardinal(
            category=self,
            kind=CardinalKind.PRODUCT,
            terms=tuple(formal_terms),
        )

    def power(self, base: Cardinal, exponent: Cardinal) -> Cardinal:
        if exponent == 0:
            return self(1)
        if base == 0:
            return self(0)
        if base == 1:
            return self(1)
        if (
            base.kind() is CardinalKind.FINITE
            and exponent.kind() is CardinalKind.FINITE
        ):
            return self(base.finite_value() ** exponent.finite_value())
        if base.is_infinite() is True and exponent.kind() is CardinalKind.FINITE:
            return base
        if (
            exponent.is_infinite() is True
            and base.kind() is CardinalKind.FINITE
            and base.finite_value() >= 2
        ):
            base = self(2)
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

    def supremum(self, *cardinal_numbers: Cardinal) -> Cardinal:
        terms: list[Cardinal] = []
        for cardinal_number in cardinal_numbers:
            if cardinal_number.kind() is CardinalKind.SUPREMUM:
                terms.extend(cardinal_number.terms())
            else:
                terms.append(cardinal_number)
        assert terms
        maximal: list[Cardinal] = []
        for candidate in sorted(set(terms), key=repr):
            if any(self.le(candidate, term) is True for term in maximal):
                continue
            maximal = [term for term in maximal if self.le(term, candidate) is not True]
            maximal.append(candidate)
        if len(maximal) == 1:
            return maximal[0]
        return Cardinal(
            category=self,
            kind=CardinalKind.SUPREMUM,
            terms=tuple(maximal),
        )

    def le(self, source: Cardinal, target: Cardinal) -> Decision:
        if source == target:
            return True
        if source.kind() is CardinalKind.SUPREMUM:
            answers = tuple(self.le(term, target) for term in source.terms())
            if all(answer is True for answer in answers):
                return True
            if any(answer is False for answer in answers):
                return False
            return UNKNOWN
        if target.kind() is CardinalKind.SUPREMUM:
            answers = tuple(self.le(source, term) for term in target.terms())
            if any(answer is True for answer in answers):
                return True
            return UNKNOWN
        if (
            source.kind() is CardinalKind.FINITE
            and target.kind() is CardinalKind.FINITE
        ):
            return source.finite_value() <= target.finite_value()
        if source.kind() is CardinalKind.FINITE and target.is_infinite() is True:
            return True
        if source.is_infinite() is True and target.kind() is CardinalKind.FINITE:
            return False
        if source.kind() is CardinalKind.ALEPH and target.kind() is CardinalKind.ALEPH:
            return source.aleph_index() <= target.aleph_index()
        if source.is_countably_infinite() and target.is_infinite() is True:
            return True
        if (
            source.kind() is CardinalKind.ALEPH
            and source.aleph_index() == 1
            and target.is_uncountable() is True
        ):
            return True
        if target.kind() is CardinalKind.POWER:
            if self.le(source, target.terms()[0]) is True:
                return True
            if (
                self.le(self(2), target.terms()[0]) is True
                and self.le(source, target.terms()[1]) is True
            ):
                return True
            if source.kind() is CardinalKind.POWER:
                base_comparison = self.le(source.terms()[0], target.terms()[0])
                exponent_comparison = self.le(
                    source.terms()[1],
                    target.terms()[1],
                )
                if base_comparison is True and exponent_comparison is True:
                    return True
        return UNKNOWN

    def lt(self, source: Cardinal, target: Cardinal) -> Decision:
        if source == target:
            return False
        less_or_equal = self.le(source, target)
        if less_or_equal is True:
            return True
        if self.le(target, source) is True:
            return False
        return UNKNOWN

    def compare(
        self,
        source: Cardinal,
        target: Cardinal,
    ) -> CardinalComparison | Unknown:
        if source == target:
            return CardinalComparison.EQUAL
        if self.lt(source, target) is True:
            return CardinalComparison.LESS
        if self.lt(target, source) is True:
            return CardinalComparison.GREATER
        return UNKNOWN

    def ge(self, source: Cardinal, target: Cardinal) -> Decision:
        return self.le(target, source)

    def gt(self, source: Cardinal, target: Cardinal) -> Decision:
        return self.lt(target, source)

    def are_incomparable(self, source: Cardinal, target: Cardinal) -> Decision:
        if self.le(source, target) is True or self.le(target, source) is True:
            return False
        return UNKNOWN

    def sum_morphism(self, *morphisms: CardinalMorphism) -> CardinalMorphism:
        sources: list[Cardinal] = []
        targets: list[Cardinal] = []
        for morphism in morphisms:
            assert morphism in self.ArrowCategory()
            source = morphism.domain()
            target = morphism.codomain()
            assert self.contains_cardinal(source)
            assert self.contains_cardinal(target)
            sources.append(source)
            targets.append(target)
        hom_category = self.Hom(self.sum(*sources), self.sum(*targets))
        assert is_cardinal_hom_category(hom_category)
        return hom_category.unique_morphism()

    def product_morphism(self, *morphisms: CardinalMorphism) -> CardinalMorphism:
        sources: list[Cardinal] = []
        targets: list[Cardinal] = []
        for morphism in morphisms:
            assert morphism in self.ArrowCategory()
            source = morphism.domain()
            target = morphism.codomain()
            assert self.contains_cardinal(source)
            assert self.contains_cardinal(target)
            sources.append(source)
            targets.append(target)
        hom_category = self.Hom(
            self.product(*sources),
            self.product(*targets),
        )
        assert is_cardinal_hom_category(hom_category)
        return hom_category.unique_morphism()

    def power_morphism(
        self,
        base_morphism: CardinalMorphism,
        exponent_morphism: CardinalMorphism,
    ) -> CardinalMorphism:
        assert base_morphism in self.ArrowCategory()
        assert exponent_morphism in self.ArrowCategory()
        source_base = base_morphism.domain()
        target_base = base_morphism.codomain()
        source_exponent = exponent_morphism.domain()
        target_exponent = exponent_morphism.codomain()
        assert self.contains_cardinal(source_base)
        assert self.contains_cardinal(target_base)
        assert self.contains_cardinal(source_exponent)
        assert self.contains_cardinal(target_exponent)
        assert self.le(self.one(), source_base) is True
        hom_category = self.Hom(
            self.power(source_base, source_exponent),
            self.power(target_base, target_exponent),
        )
        assert is_cardinal_hom_category(hom_category)
        return hom_category.unique_morphism()

    def __repr__(self) -> str:
        return "Card"


_CARDINALS = CardinalsCategory()


def Cardinals() -> CardinalsCategory:
    return _CARDINALS


def is_cardinal(value: int | Cardinal) -> TypeIs[Cardinal]:
    represented = registered_value(value)
    return represented is not None and Cardinals().contains_cardinal(represented)


def is_cardinal_hom_category(
    category: HomCategory,
) -> TypeIs[CardinalHomCategory]:
    return category in Cardinals().HomCategory()


def cardinal(value: int | Cardinal) -> Cardinal:
    if is_cardinal(value):
        return value
    return Cardinals()(value)


def aleph(index: OrdinalInput = 0) -> Cardinal:
    return Cardinals().aleph(index)


def Aleph0() -> Cardinal:
    return aleph(0)


def Continuum() -> Cardinal:
    return Cardinals().power(cardinal(2), Aleph0())


def SymbolicCardinal(name: str) -> Cardinal:
    return Cardinals().symbol(name)


def UnknownCardinality() -> Cardinal:
    return Cardinals().unknown()


aleph0 = Aleph0()
continuum = Continuum()
