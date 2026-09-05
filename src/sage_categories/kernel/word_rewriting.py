"""Finite word rewriting through GAP KBMAG.

KBMAG owns completion, reduction, and recognition of finite normal-form languages:
https://gap-packages.github.io/kbmag/doc/chap2.html
"""

from __future__ import annotations

from functools import reduce
from operator import mul

from sage_categories.kernel.sage_runtime import GapElement, libgap

__all__ = ["WordRewriter"]


class WordRewriter:
    def __init__(self, alphabet_size: int, equations: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]) -> None:
        assert libgap.LoadPackage("kbmag") == libgap.true, "GAP KBMAG is required for a presented word computation"
        self._free = libgap.FreeMonoid(alphabet_size)
        self._letters = tuple(libgap.GeneratorsOfMonoid(self._free))
        quotient = self._free / [[self._word(left), self._word(right)] for left, right in equations]
        self._system = libgap.KBMAGRewritingSystem(quotient)
        self.confluent = bool(libgap.MakeConfluent(self._system))

    def _word(self, letters: tuple[int, ...]) -> GapElement:
        return reduce(mul, (self._letters[index] for index in letters), libgap.One(self._free))

    def reduce(self, letters: tuple[int, ...]) -> tuple[int, ...]:
        result = libgap.ReducedWord(self._system, self._word(letters))
        return tuple(int(index) - 1 for index in libgap.LetterRepAssocWord(result))

    def finite(self) -> bool:
        return self.confluent and libgap.Size(self._system) != libgap.infinity
