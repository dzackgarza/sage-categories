"""Canonical objects of ``Cat()`` and finitely presented categories (D15).

``FinitePresentedCategory`` is the one implementation of every finite presented
shape: named vertices, generating edges, and rewriting relations between
composable words.  Its morphisms are the reduced words of the free category on
the graph modulo the relations; composition concatenates and reduces (nLab "free
category": objects are the vertices, morphisms the tuples of composable edges;
inspected 2026-08-26).  The writer asserts that a supplied relation system is
terminating and confluent, so reduced words are normal forms and word equality
decides morphism equality exactly.

The canonical shapes (nLab "walking structure", Kerodon 1.1; inspected 2026-08-26):

- ``[n]``: the linearly ordered set ``{0 < 1 < ... < n}`` as a category (Kerodon
  Notation 1.1.0.1, tag 0009); the free category on the linear graph
  ``0 -> 1 -> ... -> n`` is this poset category since a linear quiver has one path
  between ``i < j``;
- ``d[2]``: the free category on the 1-skeleton of the 2-simplex (Kerodon
  Construction 1.1.4.10, tag 000R: the boundary is the ``(k-1)``-skeleton);
- ``L(2, k)``: the free category on the union of all faces of the 2-simplex except
  the ``k``-th (nLab "horn"); ``L(2, 0)`` is the walking span and ``L(2, 2)`` the
  walking cospan; ``L(2, 1)`` is ``[2]`` (``cat/category.py``);
- the walking isomorphism and the walking parallel pair.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import Any

from sage_categories.cat.category import Category
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory

__all__ = [
    "FinitePresentedCategory",
    "boundary",
    "empty_category",
    "horn",
    "simplex",
    "walking_isomorphism",
    "walking_parallel_pair",
]

type Word = tuple[str, ...]
type Generator = tuple[str, Hashable, Hashable]
type Relation = tuple[Word, Word]


class Vertex(ObjectOfCategory):
    """An object of a finitely presented category: a named vertex, retained by identity."""

    def __init__(self, category: Category, label: Hashable) -> None:
        super().__init__(category)
        self._label = label

    def __repr__(self) -> str:
        return f"{self._label!r} in {self.category()!r}"


class Path(MorphismOfCategory):
    """A morphism of a finitely presented category: a reduced word of generators, first generator first."""

    def __init__(self, category: Category, domain: Vertex, codomain: Vertex, word: Word) -> None:
        super().__init__(category, domain, codomain)
        self._word = word

    def word(self) -> Word:
        return self._word

    def __repr__(self) -> str:
        if not self._word:
            return f"identity of {self.domain()!r}"
        return " then ".join(self._word)


class FinitePresentedCategory(Category):
    """The category presented by finitely many vertices, generators, and rewriting relations."""

    ObjectType = Vertex
    MorphismType = Path

    class ElementType(ElementOfObject):
        """A generalized element of a vertex; no local operation."""

    def __init__(self, name: str, labels: tuple[Hashable, ...], generators: tuple[Generator, ...], relations: tuple[Relation, ...]) -> None:
        self._name = name
        self._generator_endpoints = {generator: (source, target) for generator, source, target in generators}
        self._relations = relations
        super().__init__()
        self._vertices = {label: self.ObjectType(self, label) for label in labels}
        self._equality.register_handler(self._paths_equal)

    def __call__(self, label: Hashable) -> Vertex:
        """The retained vertex with this label."""
        return self._vertices[label]

    def label(self, vertex: Vertex) -> Hashable:
        return vertex._label

    def generator(self, name: str) -> Path:
        source, target = self._generator_endpoints[name]
        return self.construct_morphism(self(source), self(target), name)

    def _reduce(self, word: Word) -> Word:
        reduced = word
        while True:
            for left, right in self._relations:
                for start in range(len(reduced) - len(left) + 1):
                    if reduced[start : start + len(left)] == left:
                        reduced = (*reduced[:start], *right, *reduced[start + len(left) :])
                        break
                else:
                    continue
                break
            else:
                return reduced

    def construct_morphism(self, domain: Vertex, codomain: Vertex, *generators: str) -> Path:
        """The path along the named generators, reduced modulo the relations."""
        position = self.label(domain)
        for name in generators:
            source, target = self._generator_endpoints[name]
            assert source == position, f"{name} does not start at {position!r}"
            position = target
        assert position == self.label(codomain), f"the path ends at {position!r}, not at {codomain!r}"
        path = self.MorphismType(self.morphism_category(1), domain, codomain, self._reduce(generators))
        # A word in generators with declared inverses is invertible by construction.
        if path.word() and all(name in self._inverse_generators() for name in path.word()):
            refine(path, self.morphism_category(1).Isomorphisms())
        return path

    def _inverse_generators(self) -> dict[str, str]:
        return {left[0]: left[1] for left, right in self._relations if len(left) == 2 and not right}

    def construct_identity(self, vertex: Vertex) -> Path:
        return self.MorphismType(self.morphism_category(1), vertex, vertex, ())

    def element_from_defining_morphism(self, defining_morphism: Path) -> ElementOfObject:
        """The generalized element of ``codomain`` given by a path into it."""
        assert defining_morphism in self.morphism_category(1)
        return self.ElementType(defining_morphism)

    def composite(self, second: Path, first: Path) -> Path:
        assert first.codomain() is second.domain()
        return self.MorphismType(self.morphism_category(1), first.domain(), second.codomain(), self._reduce((*first.word(), *second.word())))

    def inverse_morphism(self, morphism: Path) -> Path:
        """The inverse of a path whose generators each have a declared inverse generator."""
        inverses = self._inverse_generators()
        return self.construct_morphism(morphism.codomain(), morphism.domain(), *(inverses[name] for name in reversed(morphism.word())))

    def _paths_equal(self, first: Any, second: Any) -> Decision:
        morphisms = self.morphism_category(1)
        if first not in morphisms or second not in morphisms:
            return Unknown
        return first.domain() is second.domain() and first.codomain() is second.codomain() and first.word() == second.word()

    def __repr__(self) -> str:
        return self._name


def _edge(source: int, target: int) -> Generator:
    return f"{source}->{target}", source, target


def empty_category() -> FinitePresentedCategory:
    return FinitePresentedCategory("Empty", (), (), ())


def simplex(dimension: int) -> FinitePresentedCategory:
    labels = tuple(range(dimension + 1))
    return FinitePresentedCategory(f"[{dimension}]", labels, tuple(_edge(i, i + 1) for i in range(dimension)), ())


def boundary(dimension: int) -> FinitePresentedCategory:
    assert dimension == 2
    return FinitePresentedCategory("d[2]", (0, 1, 2), (_edge(0, 1), _edge(1, 2), _edge(0, 2)), ())


def horn(dimension: int, omitted_face: int) -> FinitePresentedCategory:
    assert dimension == 2 and omitted_face in (0, 2)
    # The faces of the 2-simplex: d_0 = [1, 2], d_1 = [0, 2], d_2 = [0, 1].
    faces = {0: _edge(1, 2), 1: _edge(0, 2), 2: _edge(0, 1)}
    generators = tuple(faces[face] for face in (0, 1, 2) if face != omitted_face)
    return FinitePresentedCategory(f"L(2, {omitted_face})", (0, 1, 2), generators, ())


def walking_isomorphism() -> FinitePresentedCategory:
    return FinitePresentedCategory(
        "WalkingIsomorphism",
        (0, 1),
        (("f", 0, 1), ("g", 1, 0)),
        ((("f", "g"), ()), (("g", "f"), ())),
    )


def walking_parallel_pair() -> FinitePresentedCategory:
    return FinitePresentedCategory("WalkingParallelPair", (0, 1), (("f", 0, 1), ("g", 0, 1)), ())
