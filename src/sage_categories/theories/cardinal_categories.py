"""Cardinal numbers and their thin category.

The symbolic representation follows the cardinal-expression design in
``dzack_research.preamble.categories.sets.cardinals``. It uses no Sage
category or Sage parent.
"""

from __future__ import annotations

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
)

if TYPE_CHECKING:
    from sage_categories.theories.ordinals import Ordinal
    from sage_categories.theories.sets import SetObject


from sage_categories.theories.cardinal_values import (
    Cardinal,
    CardinalFamily,
    CardinalKind,
)


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
        assert Cardinals()._is_lequal(source, target) is True
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
        if Cardinals()._is_lequal(source, target) is True:
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

    def aleph(self, index: int | Ordinal = 0) -> Cardinal:
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
        if base.kind() is CardinalKind.FINITE and exponent.kind() is CardinalKind.FINITE:
            return self(base.finite_value() ** exponent.finite_value())
        if base.is_infinite() is True and exponent.kind() is CardinalKind.FINITE:
            return base
        if exponent.is_infinite() is True and base.kind() is CardinalKind.FINITE and base.finite_value() >= 2:
            base = self(2)
        return Cardinal(
            category=self,
            kind=CardinalKind.POWER,
            terms=(base, exponent),
        )

    def indexed_sum(
        self,
        index_set: SetObject,
        summands: CardinalFamily,
        *,
        finiteness: Decision = UNKNOWN,
    ) -> Cardinal:
        from sage_categories.theories.sets import Sets

        assert index_set in Sets()
        return Cardinal(
            category=self,
            kind=CardinalKind.INDEXED_SUM,
            index_set=index_set,
            family=summands,
            finiteness=finiteness,
        )

    def indexed_product(
        self,
        index_set: SetObject,
        factors: CardinalFamily,
        *,
        finiteness: Decision = UNKNOWN,
    ) -> Cardinal:
        from sage_categories.theories.sets import Sets

        assert index_set in Sets()
        return Cardinal(
            category=self,
            kind=CardinalKind.INDEXED_PRODUCT,
            index_set=index_set,
            family=factors,
            finiteness=finiteness,
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
            if any(self._is_lequal(candidate, term) is True for term in maximal):
                continue
            maximal = [term for term in maximal if self._is_lequal(term, candidate) is not True]
            maximal.append(candidate)
        if len(maximal) == 1:
            return maximal[0]
        return Cardinal(
            category=self,
            kind=CardinalKind.SUPREMUM,
            terms=tuple(maximal),
        )

    def _is_lequal(self, source: Cardinal, target: Cardinal) -> Decision:
        if source == target:
            return True
        if source.kind() is CardinalKind.SUPREMUM:
            return self._supremum_is_lequal(source, target)
        if target.kind() is CardinalKind.SUPREMUM:
            return self._is_lequal_to_supremum(source, target)
        size_comparison = self._compare_size_classes(source, target)
        if size_comparison is not UNKNOWN:
            return size_comparison
        if target.kind() is CardinalKind.POWER:
            return self._is_lequal_to_power(source, target)
        return UNKNOWN

    def _supremum_is_lequal(self, source: Cardinal, target: Cardinal) -> Decision:
        # A supremum is below a bound exactly when every term is.
        answers = tuple(self._is_lequal(term, target) for term in source.terms())
        if all(answer is True for answer in answers):
            return True
        if any(answer is False for answer in answers):
            return False
        return UNKNOWN

    def _is_lequal_to_supremum(self, source: Cardinal, target: Cardinal) -> Decision:
        # One term above the source suffices; no term above it decides nothing.
        if any(self._is_lequal(source, term) is True for term in target.terms()):
            return True
        return UNKNOWN

    def _compare_size_classes(self, source: Cardinal, target: Cardinal) -> Decision:
        if source.kind() is CardinalKind.FINITE and target.kind() is CardinalKind.FINITE:
            return source.finite_value() <= target.finite_value()
        if source.kind() is CardinalKind.FINITE and target.is_infinite() is True:
            return True
        if source.is_infinite() is True and target.kind() is CardinalKind.FINITE:
            return False
        if source.kind() is CardinalKind.ALEPH and target.kind() is CardinalKind.ALEPH:
            return source.aleph_index() <= target.aleph_index()
        if source.is_countably_infinite() and target.is_infinite() is True:
            return True
        if source.kind() is CardinalKind.ALEPH and source.aleph_index() == 1 and target.is_uncountable() is True:
            return True
        return UNKNOWN

    def _is_lequal_to_power(self, source: Cardinal, target: Cardinal) -> Decision:
        base, exponent = target.terms()
        if self._is_lequal(source, base) is True:
            return True
        # A base of at least two makes the power dominate its own exponent.
        if self._is_lequal(self(2), base) is True and self._is_lequal(source, exponent) is True:
            return True
        if source.kind() is CardinalKind.POWER:
            source_base, source_exponent = source.terms()
            if self._is_lequal(source_base, base) is True and self._is_lequal(source_exponent, exponent) is True:
                return True
        return UNKNOWN

    def _is_less_than(self, source: Cardinal, target: Cardinal) -> Decision:
        if source == target:
            return False
        less_or_equal = self._is_lequal(source, target)
        if less_or_equal is True:
            return True
        if self._is_lequal(target, source) is True:
            return False
        return UNKNOWN

    def are_incomparable(self, source: Cardinal, target: Cardinal) -> Decision:
        if self._is_lequal(source, target) is True or self._is_lequal(target, source) is True:
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
        assert self._is_lequal(self.one(), source_base) is True
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


def is_cardinal_hom_category(
    category: HomCategory,
) -> TypeIs[CardinalHomCategory]:
    return category in Cardinals().HomCategory()


_CARDINALS = CardinalsCategory()
