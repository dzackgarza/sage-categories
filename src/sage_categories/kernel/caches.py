"""Canonical-image tables keyed by identity.

Every canonical cache is a ``sage.structure.coerce_dict`` dictionary: keys are
compared with ``is``, held weakly, and values strongly (D12).  No cache ever calls
``__eq__`` or ``__hash__`` of an owned value.  One table per role; a key is
``(key1, key2, target category)``: objects ``(X, X, D)``, elements
``(parent, element, D)``, morphisms ``(f, f, D)`` (POL-CAT-066).

``MonoDict`` silently fails for keys that do not support weak references
(integers, strings); only owned values are ever used as its keys.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.kernel.roles import Role

if TYPE_CHECKING:
    from sage_categories.kernel.roles import CategoryPoint

__all__ = ["MonoDict", "SequenceTable", "TripleDict", "canonical_images"]

canonical_images: dict[Role, TripleDict] = {role: TripleDict(weak_values=False) for role in Role}


class _SequenceNode:
    def __init__(self) -> None:
        self.children: MonoDict = MonoDict()
        self.values: list[CategoryPoint] = []


class SequenceTable:
    """A table keyed by finite sequences of owned values, each position compared by identity.

    It retains the value chosen for a sequence form such as ``(X, Y)`` so that
    ``C.Products()((X, Y))`` and ``X * Y`` return one object (D16).
    """

    def __init__(self) -> None:
        self._root = _SequenceNode()

    def _node(self, sequence: Sequence[CategoryPoint], create: bool) -> _SequenceNode | None:
        node = self._root
        for value in sequence:
            if value not in node.children:
                if not create:
                    return None
                node.children[value] = _SequenceNode()
            node = node.children[value]
        return node

    def __contains__(self, sequence: Sequence[CategoryPoint]) -> bool:
        node = self._node(sequence, False)
        return node is not None and bool(node.values)

    def __getitem__(self, sequence: Sequence[CategoryPoint]) -> CategoryPoint:
        node = self._node(sequence, False)
        assert node is not None and node.values, f"no value is retained for {sequence!r}"
        return node.values[0]

    def __setitem__(self, sequence: Sequence[CategoryPoint], value: CategoryPoint) -> None:
        node = self._node(sequence, True)
        assert node is not None
        node.values = [value]
