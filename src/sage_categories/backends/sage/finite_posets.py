"""Sage realization functor for represented finite posets.

The computation methods delegate to Sage's mature
``sage.combinat.posets.posets.FinitePoset`` implementation.  This module owns
the engine boundary.  The public mathematical methods remain on the owned
poset category.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Protocol, TypeIs

from sage_categories.abstract_categories.functors import Functor
from sage_categories.abstract_categories.hom_categories import HomCategory
from sage_categories.category import Category
from sage_categories.theories.posets import (
    FinitePosets,
    PartiallyOrderedSets,
)
from sage_categories.theories.sets import SetElementInput
from sage_categories.values import Arrow, MathematicalObject

type PartialOrder = Callable[[SetElementInput, SetElementInput], bool]


class ExternalFinitePoset(Protocol):
    """The Sage finite-poset operations used at this boundary."""

    def is_lequal(
        self,
        left: SetElementInput,
        right: SetElementInput,
    ) -> bool: ...

    def is_less_than(
        self,
        left: SetElementInput,
        right: SetElementInput,
    ) -> bool: ...

    def compare_elements(
        self,
        left: SetElementInput,
        right: SetElementInput,
    ) -> int | None: ...

    def covers(
        self,
        lower: SetElementInput,
        upper: SetElementInput,
    ) -> bool: ...

    def lower_covers(
        self,
        member: SetElementInput,
    ) -> Iterable[SetElementInput]: ...

    def upper_covers(
        self,
        member: SetElementInput,
    ) -> Iterable[SetElementInput]: ...

    def common_lower_covers(
        self,
        members: Iterable[SetElementInput],
    ) -> Iterable[SetElementInput]: ...

    def common_upper_covers(
        self,
        members: Iterable[SetElementInput],
    ) -> Iterable[SetElementInput]: ...

    def open_interval(
        self,
        lower: SetElementInput,
        upper: SetElementInput,
    ) -> Iterable[SetElementInput]: ...

    def closed_interval(
        self,
        lower: SetElementInput,
        upper: SetElementInput,
    ) -> Iterable[SetElementInput]: ...

    def order_ideal(
        self,
        members: Iterable[SetElementInput],
    ) -> Iterable[SetElementInput]: ...

    def order_filter(
        self,
        members: Iterable[SetElementInput],
    ) -> Iterable[SetElementInput]: ...

    def minimal_elements(self) -> Iterable[SetElementInput]: ...

    def maximal_elements(self) -> Iterable[SetElementInput]: ...

    def has_bottom(self) -> bool: ...

    def bottom(self) -> SetElementInput: ...

    def has_top(self) -> bool: ...

    def top(self) -> SetElementInput: ...

    def is_bounded(self) -> bool: ...

    def height(self) -> int: ...

    def width(self) -> int: ...

    def rank(self, member: SetElementInput | None = None) -> int: ...

    def level_sets(self) -> Iterable[Iterable[SetElementInput]]: ...

    def is_ranked(self) -> bool: ...

    def is_graded(self) -> bool: ...

    def is_chain(self) -> bool: ...

    def is_chain_of_poset(
        self,
        members: Iterable[SetElementInput],
    ) -> bool: ...

    def is_antichain_of_poset(
        self,
        members: Iterable[SetElementInput],
    ) -> bool: ...


class ExternalPosetConstructor(Protocol):
    """The typed call surface of Sage's ``Poset`` constructor."""

    def __call__(
        self,
        data: tuple[tuple[SetElementInput, ...], PartialOrder],
        *,
        facade: bool,
    ) -> ExternalFinitePoset: ...


if TYPE_CHECKING:
    _sage_poset_constructor: ExternalPosetConstructor
else:
    from sage.combinat.posets.posets import Poset as _sage_poset_constructor


class SageFinitePosetObject(MathematicalObject):
    """One private Sage realization of an owned finite poset."""

    def __init__(
        self,
        *,
        category: SageFinitePosetsCategory,
        source: MathematicalObject,
    ) -> None:
        assert source in FinitePosets()
        poset = FinitePosets().first_projection()(source)
        assert PartiallyOrderedSets().contains_poset(poset)
        underlying_set = PartiallyOrderedSets().underlying_set(poset)
        assert underlying_set.is_finite() is True
        members = tuple(underlying_set)

        self._source = source
        self._value = _sage_poset_constructor((members, poset.le), facade=True)
        super().__init__(category=category)

    def source(self) -> MathematicalObject:
        return self._source

    def is_lequal(
        self,
        left: SetElementInput,
        right: SetElementInput,
    ) -> bool:
        return self._value.is_lequal(left, right)

    def is_less_than(
        self,
        left: SetElementInput,
        right: SetElementInput,
    ) -> bool:
        return self._value.is_less_than(left, right)

    def compare_elements(
        self,
        left: SetElementInput,
        right: SetElementInput,
    ) -> int | None:
        return self._value.compare_elements(left, right)

    def covers(
        self,
        lower: SetElementInput,
        upper: SetElementInput,
    ) -> bool:
        return self._value.covers(lower, upper)

    def lower_covers(self, member: SetElementInput) -> tuple[SetElementInput, ...]:
        return tuple(self._value.lower_covers(member))

    def upper_covers(self, member: SetElementInput) -> tuple[SetElementInput, ...]:
        return tuple(self._value.upper_covers(member))

    def common_lower_covers(
        self,
        members: Iterable[SetElementInput],
    ) -> tuple[SetElementInput, ...]:
        return tuple(self._value.common_lower_covers(tuple(members)))

    def common_upper_covers(
        self,
        members: Iterable[SetElementInput],
    ) -> tuple[SetElementInput, ...]:
        return tuple(self._value.common_upper_covers(tuple(members)))

    def open_interval(
        self,
        lower: SetElementInput,
        upper: SetElementInput,
    ) -> tuple[SetElementInput, ...]:
        return tuple(self._value.open_interval(lower, upper))

    def closed_interval(
        self,
        lower: SetElementInput,
        upper: SetElementInput,
    ) -> tuple[SetElementInput, ...]:
        return tuple(self._value.closed_interval(lower, upper))

    def principal_order_ideal(
        self,
        member: SetElementInput,
    ) -> tuple[SetElementInput, ...]:
        return self.order_ideal((member,))

    def principal_order_filter(
        self,
        member: SetElementInput,
    ) -> tuple[SetElementInput, ...]:
        return self.order_filter((member,))

    def order_ideal(
        self,
        members: Iterable[SetElementInput],
    ) -> tuple[SetElementInput, ...]:
        return tuple(self._value.order_ideal(tuple(members)))

    def order_filter(
        self,
        members: Iterable[SetElementInput],
    ) -> tuple[SetElementInput, ...]:
        return tuple(self._value.order_filter(tuple(members)))

    def minimal_elements(self) -> tuple[SetElementInput, ...]:
        return tuple(self._value.minimal_elements())

    def maximal_elements(self) -> tuple[SetElementInput, ...]:
        return tuple(self._value.maximal_elements())

    def has_bottom(self) -> bool:
        return self._value.has_bottom()

    def bottom(self) -> SetElementInput:
        assert self.has_bottom()
        return self._value.bottom()

    def has_top(self) -> bool:
        return self._value.has_top()

    def top(self) -> SetElementInput:
        assert self.has_top()
        return self._value.top()

    def is_bounded(self) -> bool:
        return self._value.is_bounded()

    def height(self) -> int:
        return int(self._value.height())

    def width(self) -> int:
        return int(self._value.width())

    def rank(self, member: SetElementInput | None = None) -> int:
        return int(self._value.rank(member))

    def level_sets(self) -> tuple[tuple[SetElementInput, ...], ...]:
        return tuple(tuple(level) for level in self._value.level_sets())

    def is_ranked(self) -> bool:
        return self._value.is_ranked()

    def is_graded(self) -> bool:
        return self._value.is_graded()

    def is_chain(self) -> bool:
        return self._value.is_chain()

    def is_chain_of_poset(self, members: Iterable[SetElementInput]) -> bool:
        return self._value.is_chain_of_poset(tuple(members))

    def is_antichain_of_poset(self, members: Iterable[SetElementInput]) -> bool:
        return self._value.is_antichain_of_poset(tuple(members))


class SageFinitePosetMorphism(Arrow):
    """The private realization of one finite-poset arrow."""

    def __init__(
        self,
        *,
        hom_category: SageFinitePosetHomCategory,
        source_arrow: Arrow,
    ) -> None:
        source = hom_category.domain()
        target = hom_category.codomain()
        assert is_sage_finite_poset(source)
        assert is_sage_finite_poset(target)
        assert source_arrow in FinitePosets().Hom(source.source(), target.source())
        self._source_arrow = source_arrow
        super().__init__(hom_category=hom_category)

    def source_arrow(self) -> Arrow:
        return self._source_arrow


class SageFinitePosetHomCategory(HomCategory):
    """Realizations of finite-poset arrows."""

    ObjectType = SageFinitePosetMorphism
    ElementType = SageFinitePosetMorphism

    def __call__(self, source_arrow: Arrow) -> SageFinitePosetMorphism:
        return self.ObjectType(
            hom_category=self,
            source_arrow=source_arrow,
        )

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> SageFinitePosetMorphism:
        assert value is None
        assert self.domain() is self.codomain()
        source = self.domain()
        assert is_sage_finite_poset(source)
        return self(FinitePosets().identity(source.source()))

    def compose(
        self,
        second: Arrow,
        first: Arrow,
    ) -> SageFinitePosetMorphism:
        assert is_sage_finite_poset_morphism(second)
        assert is_sage_finite_poset_morphism(first)
        assert first.codomain() is second.domain()
        return self(
            FinitePosets().compose(
                second.source_arrow(),
                first.source_arrow(),
            )
        )


class SageFinitePosetsCategory(Category):
    """Private Sage realizations of represented finite posets."""

    ObjectType = SageFinitePosetObject

    def __init__(self) -> None:
        super().__init__(object_type=SageFinitePosetObject)

    def __call__(self, source: MathematicalObject) -> SageFinitePosetObject:
        return self.ObjectType(category=self, source=source)

    def _hom_category_type(self) -> type[HomCategory]:
        return SageFinitePosetHomCategory

    def contains_realization(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SageFinitePosetObject]:
        return candidate in self

    def __repr__(self) -> str:
        return "Sage realizations of finite posets"


class SageFinitePosetRealizationFunctor(Functor):
    """Realize finite posets with Sage without supplying inheritance."""

    def __init__(self) -> None:
        self._object_images: dict[int, SageFinitePosetObject] = {}
        self._arrow_images: dict[int, SageFinitePosetMorphism] = {}
        super().__init__(FinitePosets(), SageFinitePosets())

    def on_object(self, source: MathematicalObject) -> SageFinitePosetObject:
        cached = self._object_images.get(id(source))
        if cached is None:
            cached = SageFinitePosets()(source)
            self._object_images[id(source)] = cached
        return cached

    def on_morphism(self, morphism: Arrow) -> SageFinitePosetMorphism:
        cached = self._arrow_images.get(id(morphism))
        if cached is None:
            source = self.on_object(morphism.domain())
            target = self.on_object(morphism.codomain())
            hom_category = SageFinitePosets().Hom(source, target)
            assert is_sage_finite_poset_hom_category(hom_category)
            cached = hom_category(morphism)
            self._arrow_images[id(morphism)] = cached
        return cached


_SAGE_FINITE_POSETS: SageFinitePosetsCategory | None = None
_SAGE_FINITE_POSET_REALIZATION: SageFinitePosetRealizationFunctor | None = None


def SageFinitePosets() -> SageFinitePosetsCategory:
    global _SAGE_FINITE_POSETS

    if _SAGE_FINITE_POSETS is None:
        _SAGE_FINITE_POSETS = SageFinitePosetsCategory()
    return _SAGE_FINITE_POSETS


def sage_finite_poset_realization() -> SageFinitePosetRealizationFunctor:
    global _SAGE_FINITE_POSET_REALIZATION

    if _SAGE_FINITE_POSET_REALIZATION is None:
        _SAGE_FINITE_POSET_REALIZATION = SageFinitePosetRealizationFunctor()
    return _SAGE_FINITE_POSET_REALIZATION


def realize_finite_poset(source: MathematicalObject) -> SageFinitePosetObject:
    image = sage_finite_poset_realization()(source)
    assert SageFinitePosets().contains_realization(image)
    return image


def is_sage_finite_poset(
    candidate: MathematicalObject,
) -> TypeIs[SageFinitePosetObject]:
    return SageFinitePosets().contains_realization(candidate)


def is_sage_finite_poset_hom_category(
    category: HomCategory,
) -> TypeIs[SageFinitePosetHomCategory]:
    return category.base_category() is SageFinitePosets()


def is_sage_finite_poset_morphism(
    arrow: Arrow,
) -> TypeIs[SageFinitePosetMorphism]:
    hom_category = arrow.hom_category()
    return is_sage_finite_poset_hom_category(hom_category) and arrow in hom_category
