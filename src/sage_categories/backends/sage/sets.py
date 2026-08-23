"""Owned sets whose elements have a Sage engine representation.

This adapter uses the public ``sage.structure.parent.Parent`` and
``sage.structure.element.Element`` interfaces.  Sage supplies element
construction and membership computation.  The owned ``Sets()`` category
retains all mathematical ownership.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, Protocol

from sage_categories.theories.cardinals import Cardinal
from sage_categories.theories.sets import SetElement, SetElements, SetObject, Sets
from sage_categories.values import Decision


class SageElement(Protocol):
    """The value operations required from a Sage element."""

    def __eq__(self, candidate: object) -> bool: ...

    def __hash__(self) -> int: ...

    def __repr__(self) -> str: ...


class SageParent(Protocol):
    """The parent operations required by the owned-set adapter."""

    def __contains__(self, candidate: Any) -> bool: ...

    def __repr__(self) -> str: ...


class SageSetElement(SetElement):
    """An owned set element represented by one Sage element."""

    def __init__(
        self,
        *,
        ambient_object: SageSetObject,
        sage_element: SageElement,
    ) -> None:
        self._sage_element = sage_element
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def sage_element(self) -> SageElement:
        return self._sage_element

    def __repr__(self) -> str:
        return repr(self._sage_element)


class SageSetObject(SetObject):
    """An owned set represented by a Sage parent."""

    def __init__(
        self,
        sage_parent: SageParent,
        *,
        cardinality: Cardinal | None = None,
        enumeration: Callable[[], Iterator[SageElement]] | None = None,
    ) -> None:
        self._sage_parent = sage_parent
        self._enumeration = enumeration
        self._elements: dict[SageElement, SageSetElement] = {}
        super().__init__(category=Sets(), cardinality=cardinality)

    def element(self, sage_element: SageElement) -> SageSetElement:
        assert sage_element in self._sage_parent
        cached = self._elements.get(sage_element)
        if cached is None:
            cached = SageSetElement(
                ambient_object=self,
                sage_element=sage_element,
            )
            self._elements[sage_element] = cached
        return cached

    def _membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def __iter__(self) -> Iterator[SetElement]:
        assert self._enumeration is not None, f"{self} has no chosen enumeration"
        return iter(self.element(sage_element) for sage_element in self._enumeration())

    def __repr__(self) -> str:
        return repr(self._sage_parent)


_SAGE_SET_OBJECTS: dict[int, SageSetObject] = {}


def set_from_sage(
    sage_parent: SageParent,
    *,
    cardinality: Cardinal | None = None,
    enumeration: Callable[[], Iterator[SageElement]] | None = None,
) -> SageSetObject:
    """Return the canonical owned set represented by ``sage_parent``."""
    cached = _SAGE_SET_OBJECTS.get(id(sage_parent))
    if cached is None:
        cached = SageSetObject(
            sage_parent,
            cardinality=cardinality,
            enumeration=enumeration,
        )
        _SAGE_SET_OBJECTS[id(sage_parent)] = cached
        return cached
    if cardinality is not None:
        assert cached.cardinality() == cardinality
    assert enumeration is None or cached._enumeration is enumeration
    return cached
