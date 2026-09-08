"""Native path and quotient-category computation through GAP FpCategories."""

from __future__ import annotations

from dataclasses import dataclass

from sage.libs.gap.element import GapElement
from sage.libs.gap.libgap import libgap

from sage_categories.engines.gap import FINITE_CATEGORY_PACKAGES, load_packages

__all__ = [
    "finite_morphisms",
    "native_category",
    "native_morphism",
    "native_object",
    "owned_morphism",
    "reduce_word",
]


@dataclass(frozen=True, slots=True)
class _Presentation:
    owner: object
    native: GapElement
    ambient: GapElement
    ambient_objects: tuple[GapElement, ...]
    native_objects: tuple[GapElement, ...]
    generator_names: tuple[str, ...]
    generator_indices: dict[str, int]
    quotient: bool


_presentations: dict[int, _Presentation] = {}
_loaded = False


def _load() -> None:
    global _loaded
    if not _loaded:
        load_packages(FINITE_CATEGORY_PACKAGES)
        _loaded = True


def _presentation(category: object) -> _Presentation:
    identifier = id(category)
    if identifier in _presentations:
        retained = _presentations[identifier]
        assert retained.owner is category
        return retained
    _load()
    labels = tuple(category.labels())
    names = tuple(category.generator_names())
    positions = {label: index + 1 for index, label in enumerate(labels)}
    sources = []
    targets = []
    for name in names:
        source, target = category._generator_endpoints[name]
        sources.append(positions[source])
        targets.append(positions[target])
    quiver = libgap.FinQuiver(
        [
            "sage_categories",
            [len(labels), [f"v{index}" for index in range(len(labels))]],
            [len(names), sources, targets, [f"g{index}" for index in range(len(names))]],
        ]
    )
    ambient = libgap.PathCategory(quiver)
    ambient_objects = tuple(libgap.SetOfObjects(ambient))
    generator_indices = {name: index + 1 for index, name in enumerate(names)}

    def ambient_path(source_index: int, target_index: int, word: tuple[str, ...]) -> GapElement:
        indices = [generator_indices[name] for name in word]
        return libgap.MorphismConstructor(
            ambient,
            ambient_objects[source_index],
            [len(indices), indices],
            ambient_objects[target_index],
        )

    relations = []
    for left, right in category.relations():
        witness = left or right
        if witness:
            source, target = category._path_endpoints(witness)
            assert source is not None and target is not None
        else:
            raise AssertionError("a defining relation cannot equate two empty paths")
        source_index = positions[source] - 1
        target_index = positions[target] - 1
        relations.append(
            [
                ambient_path(source_index, target_index, left),
                ambient_path(source_index, target_index, right),
            ]
        )
    native = ambient if not relations else libgap.QuotientCategory(ambient, relations)
    record = _Presentation(
        category,
        native,
        ambient,
        ambient_objects,
        tuple(libgap.SetOfObjects(native)),
        names,
        generator_indices,
        bool(relations),
    )
    _presentations[identifier] = record
    return record


def _indices(category: object, source: object, target: object) -> tuple[int, int]:
    labels = tuple(category.labels())
    return labels.index(category.label(source)), labels.index(category.label(target))


def _ambient_path(
    category: object,
    presentation: _Presentation,
    source: object,
    target: object,
    word: tuple[str, ...],
) -> GapElement:
    source_index, target_index = _indices(category, source, target)
    indices = [presentation.generator_indices[name] for name in word]
    return libgap.MorphismConstructor(
        presentation.ambient,
        presentation.ambient_objects[source_index],
        [len(indices), indices],
        presentation.ambient_objects[target_index],
    )


def _native_path(
    category: object,
    presentation: _Presentation,
    source: object,
    target: object,
    word: tuple[str, ...],
) -> GapElement:
    ambient = _ambient_path(category, presentation, source, target, word)
    if not presentation.quotient:
        return ambient
    source_index, target_index = _indices(category, source, target)
    return libgap.MorphismConstructor(
        presentation.native,
        presentation.native_objects[source_index],
        ambient,
        presentation.native_objects[target_index],
    )


def _word(presentation: _Presentation, native: GapElement) -> tuple[str, ...]:
    representative = (
        libgap.CanonicalRepresentative(native) if presentation.quotient else native
    )
    return tuple(
        presentation.generator_names[int(index) - 1]
        for index in libgap.MorphismIndices(representative)
    )


def reduce_word(
    category: object,
    source: object,
    target: object,
    word: tuple[str, ...],
) -> tuple[str, ...]:
    """Canonical FpCategories representative of one owned path."""
    presentation = _presentation(category)
    return _word(
        presentation,
        _native_path(category, presentation, source, target, word),
    )


def finite_morphisms(category: object) -> tuple[tuple[int, int, tuple[str, ...]], ...] | None:
    """Native finite Hom enumeration, or ``None`` when FpCategories proves nonfinite."""
    presentation = _presentation(category)
    if not bool(libgap.HasIsFiniteCategory(presentation.native)):
        return None
    if not bool(libgap.IsFiniteCategory(presentation.native)):
        return None
    result = []
    for native in libgap.SetOfMorphismsOfFiniteCategory(presentation.native):
        source_index = int(libgap.ObjectIndex(libgap.Source(native))) - 1
        target_index = int(libgap.ObjectIndex(libgap.Target(native))) - 1
        result.append((source_index, target_index, _word(presentation, native)))
    return tuple(result)


def native_category(category: object) -> GapElement:
    """The retained FpCategories model of one exact owned presentation."""
    return _presentation(category).native


def native_object(category: object, value: object) -> GapElement:
    """Native vertex corresponding to one exact owned vertex."""
    presentation = _presentation(category)
    index = tuple(category.labels()).index(category.label(value))
    return presentation.native_objects[index]


def native_morphism(category: object, value: object) -> GapElement:
    """Native path corresponding to one exact owned morphism."""
    presentation = _presentation(category)
    return _native_path(category, presentation, value.domain(), value.codomain(), value.word())


def owned_morphism(category: object, native: GapElement) -> object:
    """Reconstruct one owned morphism from its native path representative."""
    presentation = _presentation(category)
    source_index = int(libgap.ObjectIndex(libgap.Source(native))) - 1
    target_index = int(libgap.ObjectIndex(libgap.Target(native))) - 1
    labels = tuple(category.labels())
    return category.construct_morphism(
        category(labels[source_index]),
        category(labels[target_index]),
        _word(presentation, native),
    )
