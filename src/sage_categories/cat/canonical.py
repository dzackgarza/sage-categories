"""Canonical objects of ``Cat()`` and finitely presented categories (POL-CAT-083).

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
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category
from sage_categories.cat.declarations import Sets
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import ask
from sage_categories.kernel.refinement import refine

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = [
    "FinitePresentedCategory",
    "boundary",
    "empty_category",
    "enumerated_datum",
    "horn",
    "simplex",
    "walking_isomorphism",
    "walking_parallel_pair",
]

type Word = tuple[str, ...]
type Generator = tuple[str, Hashable, Hashable]
type Relation = tuple[Word, Word]


@dataclass(frozen=True, eq=False, slots=True)
class VertexData:
    """The local state introduced by a finitely presented vertex."""

    label: Hashable


@dataclass(frozen=True, eq=False, slots=True)
class PathData:
    """The local state introduced by a path."""

    word: Word


class FinitePresentedCategory(Category[[Word], []]):
    """The category presented by finitely many vertices, generators, and rewriting relations."""

    class ObjectType:
        """An object of a finitely presented category: a named vertex, retained by identity."""

        def __init__(self, data: VertexData) -> None:
            self._label = data.label
            super().__init__()

        def __repr__(self) -> str:
            return f"{self._label!r} in {self.category()!r}"

    class MorphismType:
        """A morphism of a finitely presented category: a reduced word of generators, first generator first."""

        def __init__(self, data: PathData) -> None:
            self._word = data.word
            super().__init__()

        def word(self) -> Word:
            return self._word

        def __repr__(self) -> str:
            if not self._word:
                return f"identity of {self.domain()!r}"
            return " then ".join(self._word)

    class ElementType:
        """A generalized element of a vertex; no local operation."""

    def __init__(self, name: str, labels: tuple[Hashable, ...], generators: tuple[Generator, ...], relations: tuple[Relation, ...]) -> None:
        self._name = name
        self._labels = labels
        self._generator_endpoints = {generator: (source, target) for generator, source, target in generators}
        self._relations = relations
        # One retained path per (source label, reduced word) (specs/functor.md, "Canonical objects of Cat"): a morphism of a
        # finitely presented category exists once by identity.
        self._paths: dict[tuple[Hashable, Word], FinitePresentedCategory.MorphismType] = {}
        self._object_set: MonoDict = MonoDict()
        self._morphism_set: MonoDict = MonoDict()
        super().__init__()
        self._vertices = {label: self.ObjectType(category=self, data=VertexData(label)) for label in labels}
        self._equality.register_handler(self._equal)

    def __call__(self, label: Hashable) -> FinitePresentedCategory.ObjectType:
        """The retained vertex with this label."""
        return self._vertices[label]

    def label(self, vertex: FinitePresentedCategory.ObjectType) -> Hashable:
        return vertex._label

    def labels(self) -> tuple[Hashable, ...]:
        """The labels of the vertices, in declaration order."""
        return self._labels

    def generator_names(self) -> tuple[str, ...]:
        """The names of the generating morphisms, in declaration order."""
        return tuple(self._generator_endpoints)

    def generator(self, name: str) -> FinitePresentedCategory.MorphismType:
        source, target = self._generator_endpoints[name]
        return self.construct_morphism(self(source), self(target), (name,))

    # -- the finite set of objects and, for an acyclic quiver, of morphisms (specs/functor.md, "Diagram shapes and universal constructions") -------
    #
    # The object set is the finite set of labels.  The morphism set is the finite
    # set of reduced words: a finite quiver without directed cycles has finitely many
    # paths (nLab "free category": the morphisms of the free category are the finite
    # composable sequences of edges; inspected 2026-08-27), so when the generator
    # graph is acyclic every morphism is reached by breadth-first extension of words,
    # and otherwise no finite enumeration of morphisms is chosen.

    def object_set(self) -> CategoryOfCategories.ElementType:
        if self not in self._object_set:
            self._object_set[self] = Sets.Finite()(self._labels)
        return self._object_set[self]

    def object_at(self, point: CategoryOfCategories.ElementType) -> FinitePresentedCategory.ObjectType:
        return self(enumerated_datum(self.object_set(), point))

    def object_point(self, vertex: FinitePresentedCategory.ObjectType) -> CategoryOfCategories.ElementType:
        return self.object_set().point(self.label(vertex))

    def _has_directed_cycle(self) -> bool:
        successors: dict[Hashable, list[Hashable]] = {label: [] for label in self._labels}
        for source, target in self._generator_endpoints.values():
            successors[source].append(target)

        def reaches(start: Hashable, stack: tuple[Hashable, ...]) -> bool:
            return any(target in stack or reaches(target, (*stack, target)) for target in successors[start])

        return any(reaches(label, (label,)) for label in self._labels)

    def _chosen_morphism_set(self) -> CategoryOfCategories.ElementType | UnknownClass:
        """The finite set of morphisms, as data ``(source label, reduced word)``, when the quiver is acyclic."""
        if self._has_directed_cycle():
            return Unknown
        if self not in self._morphism_set:
            words: list[tuple[Hashable, Word]] = [(label, ()) for label in self._labels]
            frontier = list(words)
            while frontier:
                source, word = frontier.pop(0)
                position = source if not word else self._generator_endpoints[word[-1]][1]
                for name, (start, _) in self._generator_endpoints.items():
                    if start == position:
                        extended = (source, self._reduce((*word, name)))
                        if extended not in words:
                            words.append(extended)
                            frontier.append(extended)
            self._morphism_set[self] = Sets.Finite()(words)
        return self._morphism_set[self]

    def morphism_at(self, point: CategoryOfCategories.ElementType) -> FinitePresentedCategory.MorphismType:
        source, word = enumerated_datum(ask(self.morphism_set()), point)
        target = source if not word else self._generator_endpoints[word[-1]][1]
        return self.construct_morphism(self(source), self(target), word)

    def generating_morphisms(self) -> tuple[FinitePresentedCategory.MorphismType, ...]:
        """The generators: every morphism is a composite of them."""
        return tuple(self.generator(name) for name in self._generator_endpoints)

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

    def construct_morphism(self, domain: FinitePresentedCategory.ObjectType, codomain: FinitePresentedCategory.ObjectType, word: Word) -> FinitePresentedCategory.MorphismType:
        """The path along the named generators, reduced modulo the relations."""
        position = self.label(domain)
        for name in word:
            source, target = self._generator_endpoints[name]
            assert source == position, f"{name} does not start at {position!r}"
            position = target
        assert position == self.label(codomain), f"the path ends at {position!r}, not at {codomain!r}"
        key = (self.label(domain), self._reduce(word))
        if key not in self._paths:
            path = self.MorphismType(
                category=self.morphism_category(1),
                domain=domain,
                codomain=codomain,
                data=PathData(key[1]),
            )
            # A word in generators with declared two-sided inverses is invertible by construction.
            if path.word() and all(name in self._inverse_generators() for name in path.word()):
                refine(path, self.morphism_category(1).Isomorphisms())
            self._paths[key] = path
        return self._paths[key]

    def _inverse_generators(self) -> dict[str, str]:
        """``u |-> v`` for every generator pair with both relations ``(u v) -> ()`` and ``(v u) -> ()``.

        One relation alone makes ``u`` a split monomorphism and ``v`` a split
        epimorphism, not an isomorphism (POL-MATH-042).
        """
        one_sided = {(left[0], left[1]) for left, right in self._relations if len(left) == 2 and not right}
        return {first: second for first, second in one_sided if (second, first) in one_sided}

    def construct_identity(self, vertex: FinitePresentedCategory.ObjectType) -> FinitePresentedCategory.MorphismType:
        return self.construct_morphism(vertex, vertex, ())

    def composite(self, second: FinitePresentedCategory.MorphismType, first: FinitePresentedCategory.MorphismType) -> FinitePresentedCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.construct_morphism(first.domain(), second.codomain(), (*first.word(), *second.word()))

    def inverse_morphism(self, morphism: FinitePresentedCategory.MorphismType) -> FinitePresentedCategory.MorphismType:
        """The inverse of a path whose generators each have a declared inverse generator."""
        inverses = self._inverse_generators()
        return self.construct_morphism(morphism.codomain(), morphism.domain(), tuple(inverses[name] for name in reversed(morphism.word())))

    def _equal(self, first: CategoryOfCategories.ElementType, candidate: Any) -> Decision:
        """Vertices are retained once per label, so identity decides; paths are equal exactly when their reduced words are."""
        if first in self and candidate in self:
            return first is candidate
        morphisms = self.morphism_category(1)
        if first not in morphisms or candidate not in morphisms:
            return Unknown
        return first.domain() is candidate.domain() and first.codomain() is candidate.codomain() and first.word() == candidate.word()

    def __repr__(self) -> str:
        return self._name


def enumerated_datum(
    finite_set: CategoryOfCategories.ElementType,
    point: CategoryOfCategories.ElementType,
) -> Hashable:
    """The datum of a point of a finite enumerated set, read through the chosen enumeration."""
    assert point in finite_set, f"{point!r} is not a point of {finite_set!r}"
    return next(datum for datum in Sets.Finite().chosen_enumeration(finite_set) if ask(finite_set.point(datum) == point))


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
