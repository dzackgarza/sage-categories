"""Define the private identity-key caches used by the current compiler."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import wraps
from typing import Concatenate

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.kernel.roles import CategoryPoint, role_of

__all__ = [
    "MonoDict",
    "Position",
    "SequenceTable",
    "TripleDict",
    "retained_method",
]

# A key position that is not an owned value: an index into a diagram, a chosen size, a
# truth value selecting one of two extreme cases.  Such a key carries its whole meaning and
# is compared by equality.
type Position = int | bool | str

class _SequenceNode[Value]:
    def __init__(self) -> None:
        # An owned value is compared by identity, because mathematical equality between
        # owned values is proposition-valued and can be undecided (``specs/sets.md``,
        # "Equality").  An index, a size, or a truth value carries its whole meaning and is
        # compared by equality; ``MonoDict`` cannot hold one, having no weak reference.
        self.children: MonoDict = MonoDict()
        self.indices: dict[Position, _SequenceNode[Value]] = {}
        self.values: list[Value] = []


class SequenceTable[Value]:
    """A table keyed by finite sequences, owned values by identity and positions by equality.

    It retains the value chosen for a sequence form such as ``(X, Y)`` so that
    ``C.Products()((X, Y))`` and ``X * Y`` return one object (POL-CAT-093).
    """

    def __init__(self) -> None:
        self._root: _SequenceNode[Value] = _SequenceNode()

    def _step(self, node: _SequenceNode[Value], key: CategoryPoint | Position, create: bool) -> _SequenceNode[Value] | None:
        table = node.children if role_of(key) is not None else node.indices
        if key not in table:
            if not create:
                return None
            table[key] = _SequenceNode()
        return table[key]

    def _node(self, sequence: Sequence[CategoryPoint | Position], create: bool) -> _SequenceNode[Value] | None:
        node: _SequenceNode[Value] | None = self._root
        for key in sequence:
            assert node is not None
            node = self._step(node, key, create)
            if node is None:
                return None
        return node

    def __contains__(self, sequence: Sequence[CategoryPoint | Position]) -> bool:
        node = self._node(sequence, False)
        return node is not None and bool(node.values)

    def __getitem__(self, sequence: Sequence[CategoryPoint | Position]) -> Value:
        node = self._node(sequence, False)
        assert node is not None and node.values, f"no value is retained for {sequence!r}"
        return node.values[0]

    def __setitem__(self, sequence: Sequence[CategoryPoint | Position], value: Value) -> None:
        node = self._node(sequence, True)
        assert node is not None
        node.values = [value]


def retained_method[Owner: CategoryPoint, **Arguments, Result](
    method: Callable[Concatenate[Owner, Arguments], Result],
) -> Callable[Concatenate[Owner, Arguments], Result]:
    """Retain one result of ``method`` per source value and argument sequence.

    A mathematical construction returns one value for its data: the chosen subset a
    characteristic morphism names, the direct image along a map, the ``i``-th projection of
    a product.  Calling it twice must return that value, not an equal second copy
    (POL-CAT-066).

    This is Sage's ``cached_method`` (``sage.misc.cachefunc``, inspected 2026-08-28) with
    the comparison the arguments admit.  ``cached_method`` keys its cache by equality and
    hash; equality between owned values here is a proposition that can be undecided, so it
    is not a key.  ``SequenceTable`` compares an owned argument by identity instead and an
    index or truth value by equality, and a leaf keeps no table of its own
    (``specs/resolution.md``, final decision 6).
    """
    table: SequenceTable[Result] = SequenceTable()

    @wraps(method)
    def retained(owner: Owner, *arguments: Arguments.args, **keywords: Arguments.kwargs) -> Result:
        assert not keywords, f"{method.__name__} retains its results by argument sequence and takes no keyword argument"
        key = (owner, *arguments)
        if key not in table:
            table[key] = method(owner, *arguments)
        return table[key]

    return retained
