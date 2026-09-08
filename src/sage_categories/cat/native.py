"""Owner-aware retention of private native realizations.

A computational engine may skeletonize objects or reuse one native apex in several
constructions.  The public identity is therefore always the owned value together with
its mathematical owner and construction; native identity is retained only as private
representation data.  This module stores that correspondence and performs no engine
computation, placement, or refinement.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory

__all__ = [
    "NativeMorphismRealization",
    "NativeMorphismRealizations",
    "NativeObjectRealization",
    "NativeObjectRealizations",
    "NativeUniversalPresentationRealization",
    "NativeUniversalPresentationRealizations",
    "native_universal_presentation",
    "retain_native_universal_presentation",
]

@dataclass(frozen=True, eq=False, slots=True)
class NativeObjectRealization[Native, Construction]:
    """A native representation of one exact owned object in one construction."""

    owner: Category
    value: CategoryOfCategories.ElementType
    native: Native
    construction: Construction


@dataclass(frozen=True, eq=False, slots=True)
class NativeMorphismRealization[Native]:
    """A native representation of one exact owned arrow with retained endpoints."""

    owner: Category
    value: MorphismCategory.ObjectType
    source: CategoryOfCategories.ElementType
    target: CategoryOfCategories.ElementType
    native: Native


@dataclass(frozen=True, eq=False, slots=True)
class NativeUniversalPresentationRealization[NativeDiagram, NativePresentation]:
    """Native data for one selected owned universal presentation.

    The key is the owned presentation object itself, never its apex.  The retained
    correspondence keeps the original owned diagram labels, and ``mediator`` is the
    engine's factorization operation for this already chosen native presentation.
    """

    owner: Category
    diagram: Functor
    presentation: CategoryOfCategories.ElementType
    native_diagram: NativeDiagram
    object_correspondence: tuple[tuple[CategoryOfCategories.ElementType, object], ...]
    arrow_correspondence: tuple[tuple[MorphismCategory.ObjectType, object], ...]
    native_presentation: NativePresentation
    native_apex: object
    native_legs: tuple[tuple[CategoryOfCategories.ElementType, object], ...]
    mediator: Callable[[object], object]


class _IdentityRecords[Record]:
    """Identity-keyed records that keep the key alive and never invoke its equality."""

    def __init__(self) -> None:
        self._records: dict[int, tuple[object, Record]] = {}

    def retain(self, key: object, record: Record) -> None:
        identifier = id(key)
        if identifier in self._records:
            retained_key, retained = self._records[identifier]
            assert retained_key is key
            assert retained is record, f"{key!r} already retains a different native realization"
            return
        self._records[identifier] = (key, record)

    def has(self, key: object) -> bool:
        identifier = id(key)
        return identifier in self._records and self._records[identifier][0] is key

    def get(self, key: object) -> Record:
        assert self.has(key), f"{key!r} retains no native realization"
        return self._records[id(key)][1]


class NativeObjectRealizations[Native, Construction]:
    """Native object records for one mathematical realization family."""

    def __init__(self) -> None:
        self._records: _IdentityRecords[NativeObjectRealization[Native, Construction]] = _IdentityRecords()

    def retain(
        self,
        owner: Category,
        value: CategoryOfCategories.ElementType,
        native: Native,
        construction: Construction,
    ) -> NativeObjectRealization[Native, Construction]:
        assert value in owner, f"{value!r} is not an object of {owner!r}"
        record = NativeObjectRealization(owner, value, native, construction)
        self._records.retain(value, record)
        return record

    def has(self, value: CategoryOfCategories.ElementType) -> bool:
        return self._records.has(value)

    def realization(self, value: CategoryOfCategories.ElementType) -> NativeObjectRealization[Native, Construction]:
        return self._records.get(value)


class NativeMorphismRealizations[Native]:
    """Native arrow records retaining exact mathematical owner and endpoints."""

    def __init__(self) -> None:
        self._records: _IdentityRecords[NativeMorphismRealization[Native]] = _IdentityRecords()

    def retain(
        self,
        owner: Category,
        value: MorphismCategory.ObjectType,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        native: Native,
    ) -> NativeMorphismRealization[Native]:
        hom = owner.morphism_category(1)(source, target)
        assert value in hom, f"{value!r} is not an object of the exact Hom {hom!r}"
        assert value.domain() is source and value.codomain() is target, (
            f"{value!r} does not have retained endpoints {source!r} -> {target!r}"
        )
        record = NativeMorphismRealization(owner, value, source, target, native)
        self._records.retain(value, record)
        return record

    def has(self, value: MorphismCategory.ObjectType) -> bool:
        return self._records.has(value)

    def realization(self, value: MorphismCategory.ObjectType) -> NativeMorphismRealization[Native]:
        return self._records.get(value)


class NativeUniversalPresentationRealizations[NativeDiagram, NativePresentation]:
    """Native records for selected universal presentations, keyed by presentation identity."""

    def __init__(self) -> None:
        self._records: _IdentityRecords[NativeUniversalPresentationRealization[NativeDiagram, NativePresentation]] = _IdentityRecords()

    def retain(
        self,
        owner: Category,
        diagram: Functor,
        presentation: CategoryOfCategories.ElementType,
        native_diagram: NativeDiagram,
        object_correspondence: tuple[tuple[CategoryOfCategories.ElementType, object], ...],
        arrow_correspondence: tuple[tuple[MorphismCategory.ObjectType, object], ...],
        native_presentation: NativePresentation,
        native_apex: object,
        native_legs: tuple[tuple[CategoryOfCategories.ElementType, object], ...],
        mediator: Callable[[object], object],
    ) -> NativeUniversalPresentationRealization[NativeDiagram, NativePresentation]:
        assert presentation.diagram() is diagram, f"{presentation!r} does not present {diagram!r}"
        assert presentation.apex() in owner, f"{presentation.apex()!r} is not an object of {owner!r}"
        for vertex, _ in object_correspondence:
            assert vertex in diagram.domain(), f"{vertex!r} is not a vertex of {diagram.domain()!r}"
        for arrow, _ in arrow_correspondence:
            assert arrow in diagram.domain().morphism_category(1), f"{arrow!r} is not an arrow of {diagram.domain()!r}"
        for vertex, _ in native_legs:
            assert vertex in diagram.domain(), f"{vertex!r} is not a vertex of {diagram.domain()!r}"
            presentation.leg(vertex)
        record = NativeUniversalPresentationRealization(
            owner, diagram, presentation, native_diagram, object_correspondence,
            arrow_correspondence, native_presentation, native_apex, native_legs, mediator,
        )
        self._records.retain(presentation, record)
        return record

    def has(self, presentation: CategoryOfCategories.ElementType) -> bool:
        return self._records.has(presentation)

    def realization(
        self, presentation: CategoryOfCategories.ElementType
    ) -> NativeUniversalPresentationRealization[NativeDiagram, NativePresentation]:
        return self._records.get(presentation)


_universal_presentations: NativeUniversalPresentationRealizations[object, object] = NativeUniversalPresentationRealizations()

def retain_native_universal_presentation(
    owner: Category,
    diagram: Functor,
    presentation: CategoryOfCategories.ElementType,
    native_diagram: object,
    object_correspondence: tuple[tuple[CategoryOfCategories.ElementType, object], ...],
    arrow_correspondence: tuple[tuple[MorphismCategory.ObjectType, object], ...],
    native_presentation: object,
    native_apex: object,
    native_legs: tuple[tuple[CategoryOfCategories.ElementType, object], ...],
    mediator: Callable[[object], object],
) -> NativeUniversalPresentationRealization[object, object]:
    """Retain native execution data for this exact selected universal presentation."""
    return _universal_presentations.retain(
        owner, diagram, presentation, native_diagram, object_correspondence,
        arrow_correspondence, native_presentation, native_apex, native_legs, mediator,
    )

def native_universal_presentation(
    presentation: CategoryOfCategories.ElementType,
) -> NativeUniversalPresentationRealization[object, object]:
    """Return the native realization selected by this exact owned presentation."""
    return _universal_presentations.realization(presentation)
