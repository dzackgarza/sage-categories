"""Private Sage realization of free associative algebras over ``ZZ``.

The public owner serializes a basis word as a finite tuple of generator
positions.  Sage's ``FreeAlgebra`` owns multiplication and substitution; this
module is the only place where those serializations are converted to or from
Sage free-monoid and free-algebra objects.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from sage.algebras.free_algebra import FreeAlgebra
from sage.rings.integer_ring import ZZ

type Word = tuple[int, ...]
type Terms = Mapping[Word, int]


def integer_free_algebra(names: Sequence[str]):
    """Return Sage's free associative algebra ``ZZ<names>``."""
    names = tuple(str(name) for name in names)
    return FreeAlgebra(ZZ, len(names), names)


def _native_word(algebra, word: Word):
    if not word:
        return algebra.monoid().one()
    return algebra.monoid()([(int(position), 1) for position in word])


def _word(native_word) -> Word:
    generators = {generator: position for position, generator in enumerate(native_word.parent().gens())}
    return tuple(generators[generator] for generator in native_word.to_list())


def _element(algebra, terms: Terms):
    return algebra.sum_of_terms(
        ((_native_word(algebra, word), ZZ(int(coefficient))) for word, coefficient in terms.items() if int(coefficient) != 0),
        distinct=True,
    )


def coefficients(algebra, element) -> dict[Word, int]:
    """Serialize one native free-algebra element in the word basis."""
    assert element.parent() is algebra
    return {_word(word): int(coefficient) for word, coefficient in element.monomial_coefficients(copy=False).items() if int(coefficient) != 0}


def multiply(algebra, left: Terms, right: Terms) -> dict[Word, int]:
    """Multiply two serialized elements through Sage's free algebra."""
    return coefficients(algebra, _element(algebra, left) * _element(algebra, right))


def substitute(
    algebra,
    element: Terms,
    images: Sequence[Terms],
) -> dict[Word, int]:
    """Evaluate one serialized element at serialized generator images."""
    native_images = tuple(_element(algebra, image) for image in images)
    return coefficients(algebra, _element(algebra, element)(*native_images))


def generator(algebra, position: int) -> dict[Word, int]:
    return coefficients(algebra, algebra.gen(int(position)))


def one(algebra) -> dict[Word, int]:
    return coefficients(algebra, algebra.one())


__all__ = [
    "coefficients",
    "generator",
    "integer_free_algebra",
    "multiply",
    "one",
    "substitute",
]
