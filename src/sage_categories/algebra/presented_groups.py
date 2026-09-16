"""Native finitely presented groups with their owned group objects and universal maps.

A presentation ``<x_i | r_j>`` retains Sage/GAP's native free group, relation
homomorphism, quotient group and quotient map.  Public group objects remain objects of
``Groups(Cartesian(Sets))``; the native parents are private computation engines and the
carrier sets are rule-defined, never enumerated.
"""

from __future__ import annotations

__all__ = ["GroupPresentation", "presented_group"]

from collections.abc import Sequence

from sympy import false, true

from sage_categories.algebra._firewall import presented_groups as _backend
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.certified_structures import certified_group
from sage_categories.cat.monoidal import Cartesian
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import (
    Magmas,
    Monoids,
    PointedMagmas,
)
from sage_categories.sets import Sets

type GroupWord = tuple[int, ...]


def _owned_group(owner: object, role: str):
    """Raise one native group parent to the existing category of group objects."""
    structure = Cartesian(Sets)
    carrier = Sets.from_membership(lambda value: true if _backend.is_member(owner, role, value) else false)
    square = binary_product_data(Sets, carrier, carrier).apex()
    multiplication = Mor(Sets)(square, carrier)(lambda pair: _backend.multiply(pair[0], pair[1]))
    unit = Mor(Sets)(structure.unit(), carrier)(lambda _: _backend.one(owner, role))
    inverse_shear = Mor(Sets)(square, square)(lambda pair: _backend.inverse_product(pair[0], pair[1]))
    return certified_group(carrier, multiplication, unit, inverse_shear, structure)


def _owned_group_homomorphism(source, target, native):
    """Raise a native group homomorphism to the existing full group subcategory."""
    structure = Cartesian(Sets)
    source_carrier = source.operation().codomain()
    target_carrier = target.operation().codomain()
    underlying = Mor(Sets)(source_carrier, target_carrier)(lambda value: _backend.apply_map(native, value))
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
    return monoid_map


class GroupPresentation:
    """One native group presentation ``<x_i | r_j>`` and its universal quotient."""

    def __init__(self, generator_names: Sequence[str], relations: Sequence[GroupWord]) -> None:
        names = tuple(str(name) for name in generator_names)
        if not names:
            raise ValueError("a represented group presentation requires at least one generator")
        if len(set(names)) != len(names):
            raise ValueError("group presentation generator names are distinct")
        relation_words = tuple(tuple(int(letter) for letter in word) for word in relations)
        self._generator_names = names
        self._relation_words = relation_words
        _backend.prepare(self, names, relation_words)
        self._free_group = _owned_group(self, "free")
        self._relation_group = _owned_group(self, "relations")
        self._group = _owned_group(self, "quotient")
        self._relation_arrow = _owned_group_homomorphism(self._relation_group, self._free_group, _backend.native_map(self, "relations"))
        self._trivial_relation_arrow = _owned_group_homomorphism(
            self._relation_group,
            self._free_group,
            _backend.native_map(self, "trivial-relations"),
        )
        self._quotient_morphism = _owned_group_homomorphism(self._free_group, self._group, _backend.native_map(self, "quotient"))

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
        return tuple(self.free_group().point(value) for value in _backend.generators(self, "free"))

    def generators(self):
        return tuple(self.group().point(value) for value in _backend.generators(self, "quotient"))

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
        generators = tuple(self.relation_group().point(value) for value in _backend.generators(self, "relations"))
        return tuple(self.relation_arrow()(generator) for generator in generators)

    def evaluate_word(self, word: GroupWord):
        return self.group().point(_backend.evaluate_word(self, "quotient", tuple(word)))

    def factor(self, target, generator_images):
        """Factor a relation-respecting assignment uniquely through the quotient.

        Sage/GAP's native finitely-presented-group homomorphism constructor checks the
        relators.  A violated relation therefore raises ``ValueError`` without a second
        repository-owned evaluator.
        """
        target_carrier = target.operation().codomain()
        points = tuple(generator_images)
        if any(point.parent() is not target_carrier for point in points):
            raise ValueError("presentation generator images must be points of the target group carrier")
        images = tuple(point.datum() for point in points)
        if len(images) != len(self.generator_names()):
            raise ValueError("one target image is required for every presentation generator")
        native = _backend.factor_map(self, images)
        return _owned_group_homomorphism(self.group(), target, native)

    def __repr__(self) -> str:
        return _backend.representation(self)


def presented_group(generator_names: Sequence[str], relations: Sequence[GroupWord] = ()) -> GroupPresentation:
    return GroupPresentation(generator_names, relations)
