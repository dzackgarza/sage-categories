"""Native finitely presented groups with their owned group objects and universal maps.

A presentation ``<x_i | r_j>`` retains Sage/GAP's native free group, relation
homomorphism, quotient group and quotient map.  Public group objects remain objects of
``Groups(Cartesian(Sets))``; the native parents are private computation engines and the
carrier sets are rule-defined, never enumerated.
"""

from __future__ import annotations

__all__ = ["GroupPresentation", "presented_group"]

from collections.abc import Sequence

from sage.groups.free_group import FreeGroup
from sage.structure.sage_object import SageObject
from sympy import false, true

from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.monoidal import Cartesian
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import (
    Groups,
    Magmas,
    Monoids,
    PointedMagmas,
    _shear,
)
from sage_categories.kernel.refinement import refine
from sage_categories.sets import Sets

type GroupWord = tuple[int, ...]


def _native_parent_is(engine, value) -> bool:
    return getattr(value, "parent", lambda: None)() is engine


def _native_word(engine, word: GroupWord):
    """Construct a word through Sage/GAP's native Tietze-word constructor."""
    return engine(tuple(int(letter) for letter in word))


def _owned_group(engine):
    """Raise one native group parent to the existing category of group objects."""
    structure = Cartesian(Sets)
    carrier = Sets.from_membership(lambda value: true if _native_parent_is(engine, value) else false)
    square = binary_product_data(Sets, carrier, carrier).apex()
    multiplication = Mor(Sets)(square, carrier)(lambda pair: pair[0] * pair[1])
    unit = Mor(Sets)(structure.unit(), carrier)(lambda _: engine.one())
    magma = Magmas(structure).algebra(carrier, multiplication)
    pointed = PointedMagmas(structure.tensor(), structure.unit()).algebra(magma, unit)
    # The native group parent is the theorem supplying associativity, units and inverses;
    # refinement installs those already-defined structure-category roles without asking
    # an infinite carrier to prove the laws by enumeration.
    refine(pointed, Monoids(structure))
    refine(pointed, Groups(structure))

    shear = _shear(pointed)
    inverse_shear = Mor(Sets)(square, square)(lambda pair: (pair[0], pair[0] ** -1 * pair[1]))
    Sets.retain_inverses(shear, inverse_shear)
    pointed._native_group_engine = engine
    return pointed


def _native_engine(group):
    engine = getattr(group, "_native_group_engine", None)
    if engine is None:
        raise TypeError("this group object has no retained native group realization")
    return engine


def _owned_group_homomorphism(source, target, native):
    """Raise a native group homomorphism to the existing full group subcategory."""
    structure = Cartesian(Sets)
    source_carrier = source.operation().codomain()
    target_carrier = target.operation().codomain()
    underlying = Mor(Sets)(source_carrier, target_carrier)(lambda value: native(value))
    to_magmas = Monoids(structure).to_magmas()
    magma_map = Magmas(structure).homomorphism(
        to_magmas.on_object(source),
        to_magmas.on_object(target),
        underlying,
    )
    monoid_map = PointedMagmas(structure.tensor(), structure.unit()).homomorphism(
        source,
        target,
        magma_map,
    )
    monoid_map._native_group_homomorphism = native
    return monoid_map


class GroupPresentation(SageObject):
    """One native group presentation ``<x_i | r_j>`` and its universal quotient."""

    def __init__(self, generator_names: Sequence[str], relations: Sequence[GroupWord]) -> None:
        names = tuple(str(name) for name in generator_names)
        if not names:
            raise ValueError("a represented group presentation requires at least one generator")
        if len(set(names)) != len(names):
            raise ValueError("group presentation generator names are distinct")
        relation_words = tuple(tuple(int(letter) for letter in word) for word in relations)
        free = FreeGroup(names)
        native_relations = tuple(_native_word(free, word) for word in relation_words)
        quotient = free / native_relations

        relation_free = FreeGroup(tuple(f"r{index}" for index in range(len(native_relations))))
        relation_arrow_native = relation_free.hom(native_relations, free)
        trivial_relation_native = relation_free.hom([free.one() for _ in native_relations], free)
        quotient_native = free.hom(tuple(quotient.gens()), quotient)

        self._generator_names = names
        self._relation_words = relation_words
        self._free_engine = free
        self._relation_engine = relation_free
        self._quotient_engine = quotient
        self._free_group = _owned_group(free)
        self._relation_group = _owned_group(relation_free)
        self._group = _owned_group(quotient)
        self._relation_arrow = _owned_group_homomorphism(self._relation_group, self._free_group, relation_arrow_native)
        self._trivial_relation_arrow = _owned_group_homomorphism(self._relation_group, self._free_group, trivial_relation_native)
        self._quotient_morphism = _owned_group_homomorphism(self._free_group, self._group, quotient_native)

    def generator_names(self) -> tuple[str, ...]:
        return self._generator_names

    def relation_words(self) -> tuple[GroupWord, ...]:
        return self._relation_words

    def free_group(self):
        return self._free_group

    def relation_group(self):
        return self._relation_group

    def group(self):
        return self._group

    def free_generators(self):
        return tuple(self.free_group().point(value) for value in self._free_engine.gens())

    def generators(self):
        return tuple(self.group().point(value) for value in self._quotient_engine.gens())

    def relation_arrow(self):
        """The native map from the free group on relation symbols to the free group."""
        return self._relation_arrow

    def trivial_relation_arrow(self):
        """The parallel map sending every relation symbol to the identity."""
        return self._trivial_relation_arrow

    def quotient_morphism(self):
        """The selected quotient ``F(x_i) -> <x_i | r_j>``."""
        return self._quotient_morphism

    def relation_images(self):
        generators = tuple(self.relation_group().point(value) for value in self._relation_engine.gens())
        return tuple(self.relation_arrow()(generator) for generator in generators)

    def evaluate_word(self, word: GroupWord):
        return self.group().point(_native_word(self._quotient_engine, tuple(word)))

    def factor(self, target, generator_images):
        """Factor a relation-respecting assignment uniquely through the quotient.

        Sage/GAP's native finitely-presented-group homomorphism constructor checks the
        relators.  A violated relation therefore raises ``ValueError`` rather than being
        accepted by a second local word evaluator.
        """
        target_carrier = target.operation().codomain()
        points = tuple(generator_images)
        if any(point.parent() is not target_carrier for point in points):
            raise ValueError("presentation generator images must be points of the target group carrier")
        images = tuple(point.datum() for point in points)
        if len(images) != len(self.generator_names()):
            raise ValueError("one target image is required for every presentation generator")
        native = self._quotient_engine.hom(images, _native_engine(target))
        return _owned_group_homomorphism(self.group(), target, native)

    def _repr_(self) -> str:
        return repr(self._quotient_engine)


def presented_group(generator_names: Sequence[str], relations: Sequence[GroupWord] = ()) -> GroupPresentation:
    return GroupPresentation(generator_names, relations)
