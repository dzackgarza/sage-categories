"""Canonical-image tables keyed by identity.

Every canonical cache is a ``sage.structure.coerce_dict`` dictionary.  Keys use
identity and values are retained strongly (POL-KERNEL-001).  The outer table is
keyed by the target category.  The inner identity key is the exact public role
data required by POL-CAT-066: ``(X, X, X)`` for an object,
``(stage, defining morphism, codomain)`` for an element, and
``(domain, codomain, f)`` for a morphism.

``MonoDict`` silently fails for keys that do not support weak references
(integers, strings); only owned values are ever used as its keys.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, overload

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.kernel.construction import ElementConstructionInput, MorphismConstructionInput, ObjectConstructionInput
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = [
    "MonoDict",
    "SequenceTable",
    "TripleDict",
    "canonical_images",
    "canonical_input",
    "canonical_inputs",
    "has_canonical_transport",
    "retain_canonical_transport",
    "retain_constructed_transport",
]

# One target-indexed table per role.  Keeping the target outside the inner
# TripleDict leaves all three identity components available for the mathematical
# source key.
canonical_images: dict[Role, MonoDict] = {role: MonoDict() for role in Role}
canonical_inputs: dict[Role, MonoDict] = {role: MonoDict() for role in Role}


def _target_table(tables: dict[Role, MonoDict], role: Role, target: Category) -> TripleDict:
    by_target = tables[role]
    if target not in by_target:
        by_target[target] = TripleDict(weak_values=False)
    return by_target[target]


def _source_key(source: CategoryPoint) -> tuple[CategoryPoint, CategoryPoint, CategoryPoint]:
    match role_of(source):
        case Role.OBJECT:
            return source, source, source
        case Role.ELEMENT:
            assert isinstance(source, ElementOfObject)
            return source.stage(), source.defining_morphism(), source.parent()
        case Role.MORPHISM:
            assert isinstance(source, MorphismOfCategory)
            return source.domain(), source.codomain(), source
    raise AssertionError(f"{source!r} is not an owned value")


def _construction_key[
    ObjectValue: ObjectOfCategory,
    ElementValue: ElementOfObject,
    MorphismValue: MorphismOfCategory,
    Datum,
](
    source: ObjectConstructionInput[ObjectValue, Datum]
    | ElementConstructionInput[ElementValue, Datum]
    | MorphismConstructionInput[MorphismValue, Datum],
) -> tuple[CategoryPoint, CategoryPoint, CategoryPoint]:
    """The source identity key before its public value has run its initializer."""
    if isinstance(source, ObjectConstructionInput):
        return source.canonical_image, source.canonical_image, source.canonical_image
    if isinstance(source, ElementConstructionInput):
        defining = source.identity.defining_morphism
        return defining.domain(), defining, defining.codomain()
    return source.identity.domain, source.identity.codomain, source.canonical_image


def _retain_at_key[
    ObjectValue: ObjectOfCategory,
    ElementValue: ElementOfObject,
    MorphismValue: MorphismOfCategory,
    Datum,
](
    role: Role,
    key: tuple[CategoryPoint, CategoryPoint, CategoryPoint],
    target: Category,
    image: CategoryPoint,
    construction: ObjectConstructionInput[ObjectValue, Datum]
    | ElementConstructionInput[ElementValue, Datum]
    | MorphismConstructionInput[MorphismValue, Datum],
) -> None:
    images = _target_table(canonical_images, role, target)
    inputs = _target_table(canonical_inputs, role, target)
    if key in images:
        assert images[key] is image and inputs[key] is construction
        return
    images[key] = image
    inputs[key] = construction


def has_canonical_transport(source: CategoryPoint, target: Category) -> bool:
    """Whether the exact source data already retains an image and input at ``target``."""
    role = role_of(source)
    assert role is not None
    by_target = canonical_images[role]
    return target in by_target and _source_key(source) in by_target[target]


@overload
def canonical_input[TargetValue: ObjectOfCategory, Datum](
    source: ObjectOfCategory,
    target: Category,
) -> ObjectConstructionInput[TargetValue, Datum]: ...


@overload
def canonical_input[TargetValue: ElementOfObject, Datum](
    source: ElementOfObject,
    target: Category,
) -> ElementConstructionInput[TargetValue, Datum]: ...


@overload
def canonical_input[TargetValue: MorphismOfCategory, Datum](
    source: MorphismOfCategory,
    target: Category,
) -> MorphismConstructionInput[TargetValue, Datum]: ...


def canonical_input[
    ObjectValue: ObjectOfCategory,
    ElementValue: ElementOfObject,
    MorphismValue: MorphismOfCategory,
    Datum,
](
    source: CategoryPoint,
    target: Category,
) -> ObjectConstructionInput[ObjectValue, Datum] | ElementConstructionInput[ElementValue, Datum] | MorphismConstructionInput[MorphismValue, Datum]:
    """The construction input retained with the canonical image at ``target``."""
    role = role_of(source)
    assert role is not None
    by_target = canonical_inputs[role]
    assert target in by_target and _source_key(source) in by_target[target]
    return by_target[target][_source_key(source)]


@overload
def retain_canonical_transport[Value: ObjectOfCategory, Datum](
    source: ObjectOfCategory,
    target: Category,
    image: Value,
    construction: ObjectConstructionInput[Value, Datum],
) -> None: ...


@overload
def retain_canonical_transport[Value: ElementOfObject, Datum](
    source: ElementOfObject,
    target: Category,
    image: Value,
    construction: ElementConstructionInput[Value, Datum],
) -> None: ...


@overload
def retain_canonical_transport[Value: MorphismOfCategory, Datum](
    source: MorphismOfCategory,
    target: Category,
    image: Value,
    construction: MorphismConstructionInput[Value, Datum],
) -> None: ...


def retain_canonical_transport[
    ObjectValue: ObjectOfCategory,
    ElementValue: ElementOfObject,
    MorphismValue: MorphismOfCategory,
    Datum,
](
    source: CategoryPoint,
    target: Category,
    image: CategoryPoint,
    construction: ObjectConstructionInput[ObjectValue, Datum]
    | ElementConstructionInput[ElementValue, Datum]
    | MorphismConstructionInput[MorphismValue, Datum],
) -> None:
    """Retain one canonical image and its exact construction input by identity."""
    role = role_of(source)
    assert role is not None and role_of(image) is role
    _retain_at_key(role, _source_key(source), target, image, construction)


@overload
def retain_constructed_transport[
    SourceValue: ObjectOfCategory,
    SourceDatum,
    TargetValue: ObjectOfCategory,
    TargetDatum,
](
    source: ObjectConstructionInput[SourceValue, SourceDatum],
    target: Category,
    construction: ObjectConstructionInput[TargetValue, TargetDatum],
) -> None: ...


@overload
def retain_constructed_transport[
    SourceValue: ElementOfObject,
    SourceDatum,
    TargetValue: ElementOfObject,
    TargetDatum,
](
    source: ElementConstructionInput[SourceValue, SourceDatum],
    target: Category,
    construction: ElementConstructionInput[TargetValue, TargetDatum],
) -> None: ...


@overload
def retain_constructed_transport[
    SourceValue: MorphismOfCategory,
    SourceDatum,
    TargetValue: MorphismOfCategory,
    TargetDatum,
](
    source: MorphismConstructionInput[SourceValue, SourceDatum],
    target: Category,
    construction: MorphismConstructionInput[TargetValue, TargetDatum],
) -> None: ...


def retain_constructed_transport[
    SourceObjectValue: ObjectOfCategory,
    SourceElementValue: ElementOfObject,
    SourceMorphismValue: MorphismOfCategory,
    SourceDatum,
    TargetObjectValue: ObjectOfCategory,
    TargetElementValue: ElementOfObject,
    TargetMorphismValue: MorphismOfCategory,
    TargetDatum,
](
    source: ObjectConstructionInput[SourceObjectValue, SourceDatum]
    | ElementConstructionInput[SourceElementValue, SourceDatum]
    | MorphismConstructionInput[SourceMorphismValue, SourceDatum],
    target: Category,
    construction: ObjectConstructionInput[TargetObjectValue, TargetDatum]
    | ElementConstructionInput[TargetElementValue, TargetDatum]
    | MorphismConstructionInput[TargetMorphismValue, TargetDatum],
) -> None:
    """Retain an ancestor input before the source initializer starts (specs/resolution.md, final decision 14)."""
    if isinstance(source, ObjectConstructionInput):
        assert isinstance(construction, ObjectConstructionInput)
        role = Role.OBJECT
    elif isinstance(source, ElementConstructionInput):
        assert isinstance(construction, ElementConstructionInput)
        role = Role.ELEMENT
    else:
        assert isinstance(construction, MorphismConstructionInput)
        role = Role.MORPHISM
    _retain_at_key(role, _construction_key(source), target, construction.canonical_image, construction)


class _SequenceNode:
    def __init__(self) -> None:
        self.children: MonoDict = MonoDict()
        self.values: list[CategoryPoint] = []


class SequenceTable:
    """A table keyed by finite sequences of owned values, each position compared by identity.

    It retains the value chosen for a sequence form such as ``(X, Y)`` so that
    ``C.Products()((X, Y))`` and ``X * Y`` return one object (POL-CAT-093).
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
