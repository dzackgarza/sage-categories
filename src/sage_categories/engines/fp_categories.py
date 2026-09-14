"""Native path and quotient-category computation through GAP FpCategories."""

from __future__ import annotations

from dataclasses import dataclass

from sage.libs.gap.element import GapElement
from sage.libs.gap.libgap import libgap
from sage.libs.gap.util import GAPError

from sage_categories.engines.gap import FINITE_CATEGORY_PACKAGES, load_packages
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

__all__ = [
    "compose_morphisms",
    "finite_morphisms",
    "inverse_morphism",
    "is_isomorphism",
    "native_category",
    "native_morphism",
    "native_object",
    "owned_morphism",
    "owned_object",
    "reduce_word",
    "terminal_object",
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


def _ambient_native_path(
    ambient: GapElement,
    ambient_objects: tuple[GapElement, ...],
    generator_indices: dict[str, int],
    source_index: int,
    target_index: int,
    word: tuple[str, ...],
) -> GapElement:
    """Construct one typed path in the retained ambient path category."""
    indices = [generator_indices[name] for name in word]
    return libgap.MorphismConstructor(
        ambient,
        ambient_objects[source_index],
        [len(indices), indices],
        ambient_objects[target_index],
    )


def _ambient_presentation(
    category: object,
) -> tuple[
    tuple[str, ...],
    dict[object, int],
    GapElement,
    tuple[GapElement, ...],
    dict[str, int],
]:
    """Lower the objects and generators of one owned presentation to a GAP path category."""
    labels = tuple(category.labels())
    names = tuple(category.generator_names())
    positions = {label: index + 1 for index, label in enumerate(labels)}
    endpoints = tuple(tuple(category.label(endpoint) for endpoint in category.generator_endpoints(name)) for name in names)
    quiver = libgap.FinQuiver(
        [
            "sage_categories",
            [len(labels), [f"v{index}" for index in range(len(labels))]],
            [
                len(names),
                [positions[source] for source, _target in endpoints],
                [positions[target] for _source, target in endpoints],
                [f"g{index}" for index in range(len(names))],
            ],
        ]
    )
    ambient = libgap.PathCategory(quiver)
    return (
        names,
        positions,
        ambient,
        tuple(libgap.SetOfObjects(ambient)),
        {name: index + 1 for index, name in enumerate(names)},
    )


def _defining_relations(
    category: object,
    positions: dict[object, int],
    ambient: GapElement,
    ambient_objects: tuple[GapElement, ...],
    generator_indices: dict[str, int],
) -> list[list[GapElement]]:
    """Lower the owned path equations to typed relations in the ambient path category."""
    relations: list[list[GapElement]] = []
    for left, right in category.relations():
        witness = left or right
        if not witness:
            raise AssertionError("a defining relation cannot equate two empty paths")
        source = category.label(category.generator_endpoints(witness[0])[0])
        target = category.label(category.generator_endpoints(witness[-1])[1])
        source_index = positions[source] - 1
        target_index = positions[target] - 1
        relations.append(
            [
                _ambient_native_path(ambient, ambient_objects, generator_indices, source_index, target_index, left),
                _ambient_native_path(ambient, ambient_objects, generator_indices, source_index, target_index, right),
            ]
        )
    return relations


@cached_function(key=identity_key)
def _presentation(category: object) -> _Presentation:
    load_packages(FINITE_CATEGORY_PACKAGES)
    names, positions, ambient, ambient_objects, generator_indices = _ambient_presentation(category)
    relations = _defining_relations(category, positions, ambient, ambient_objects, generator_indices)
    native = ambient if not relations else libgap.QuotientCategory(ambient, relations)
    return _Presentation(
        category,
        native,
        ambient,
        ambient_objects,
        tuple(libgap.SetOfObjects(native)),
        names,
        generator_indices,
        bool(relations),
    )


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
    return _ambient_native_path(
        presentation.ambient,
        presentation.ambient_objects,
        presentation.generator_indices,
        source_index,
        target_index,
        word,
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
    representative = libgap.CanonicalRepresentative(native) if presentation.quotient else native
    return tuple(presentation.generator_names[int(index) - 1] for index in libgap.MorphismIndices(representative))


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


def compose_morphisms(category: object, second: object, first: object) -> object:
    """Compose two owned paths through the native ``FpCategories`` category."""
    assert first.codomain() is second.domain()
    native = libgap.PreCompose(
        native_morphism(category, first),
        native_morphism(category, second),
    )
    return owned_morphism(category, native)


def inverse_morphism(category: object, morphism: object) -> object:
    """Reconstruct the inverse supplied by the native presented category."""
    return owned_morphism(category, libgap.Inverse(native_morphism(category, morphism)))


def is_isomorphism(category: object, morphism: object) -> bool | None:
    """Native isomorphism decision when ``FpCategories`` has an applicable method."""
    try:
        return bool(libgap.IsIsomorphism(native_morphism(category, morphism)))
    except GAPError as error:
        # ``ApplicableMethod`` is not a safe preflight here: GAP documents that an
        # applicable method may still ``TryNextMethod``.  Let GAP perform its own full
        # dispatch, and preserve undecidability only when that chain has no method.
        if "no method found" in str(error):
            return None
        raise


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


def owned_object(category: object, native: GapElement) -> object:
    """Reconstruct one owned vertex from its native FpCategories object."""
    index = int(libgap.ObjectIndex(native)) - 1
    return category(tuple(category.labels())[index])


def terminal_object(category: object) -> object | None:
    """Choose the first native-certified terminal vertex, if one exists."""
    presentation = _presentation(category)
    if not bool(libgap.HasIsFiniteCategory(presentation.native)):
        return None
    if not bool(libgap.IsFiniteCategory(presentation.native)):
        return None
    for target in presentation.native_objects:
        if all(len(libgap.MorphismsOfExternalHom(source, target)) == 1 for source in presentation.native_objects):
            return owned_object(category, target)
    return None


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
