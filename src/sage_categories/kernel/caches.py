"""Canonical-image tables keyed by identity.

Every canonical cache is a ``sage.structure.coerce_dict`` dictionary.  Keys use
identity and values are retained strongly (POL-KERNEL-001).  The outer table is
keyed by the target category.  The inner identity key is the exact public role
data required by POL-CAT-066: ``(X, X, X)`` for an object,
``(domain, defining morphism, codomain)`` for an element, and
``(domain, codomain, f)`` for a morphism.

``MonoDict`` silently fails for keys that do not support weak references
(integers, strings); only owned values are ever used as its keys.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import wraps
from typing import TYPE_CHECKING, Concatenate, overload

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.kernel.construction import (
    ElementConstructionInput,
    ElementRoleIdentity,
    MorphismConstructionInput,
    ObjectConstructionInput,
)
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = [
    "MonoDict",
    "Position",
    "SequenceTable",
    "TripleDict",
    "canonical_images",
    "canonical_input",
    "canonical_inputs",
    "has_canonical_transport",
    "retain_canonical_transport",
    "retain_constructed_transport",
    "retained_method",
]

# A key position that is not an owned value: an index into a diagram, a chosen size, a
# truth value selecting one of two extreme cases.  Such a key carries its whole meaning and
# is compared by equality.
type Position = int | bool | str

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
            return source.defining_morphism().domain(), source.defining_morphism(), source.parent()
        case Role.MORPHISM:
            assert isinstance(source, MorphismOfCategory)
            return source.domain(), source.codomain(), source
    raise AssertionError(f"{source!r} is not an owned value")


def _construction_key[
    ObjectValue: ObjectOfCategory,
    ElementValue: CategoryPoint,
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
        assert isinstance(source.identity, ElementRoleIdentity)
        defining = source.identity.defining_morphism
        return defining.domain(), defining, defining.codomain()
    return source.identity.domain, source.identity.codomain, source.canonical_image


def _retain_at_key[
    ObjectValue: ObjectOfCategory,
    ElementValue: CategoryPoint,
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


@overload
def canonical_input[
    ObjectValue: ObjectOfCategory,
    ElementValue: CategoryPoint,
    MorphismValue: MorphismOfCategory,
    Datum,
](
    source: CategoryPoint,
    target: Category,
) -> ObjectConstructionInput[ObjectValue, Datum] | ElementConstructionInput[ElementValue, Datum] | MorphismConstructionInput[MorphismValue, Datum]: ...


def canonical_input[
    ObjectValue: ObjectOfCategory,
    ElementValue: CategoryPoint,
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


@overload
def retain_canonical_transport[
    ObjectValue: ObjectOfCategory,
    ElementValue: CategoryPoint,
    MorphismValue: MorphismOfCategory,
    Datum,
](
    source: CategoryPoint,
    target: Category,
    image: CategoryPoint,
    construction: ObjectConstructionInput[ObjectValue, Datum]
    | ElementConstructionInput[ElementValue, Datum]
    | MorphismConstructionInput[MorphismValue, Datum],
) -> None: ...


def retain_canonical_transport[
    ObjectValue: ObjectOfCategory,
    ElementValue: CategoryPoint,
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
    TargetMorphismValue: MorphismOfCategory,
    TargetDatum,
](
    source: ObjectConstructionInput[SourceValue, SourceDatum],
    target: Category,
    construction: ObjectConstructionInput[TargetValue, TargetDatum] | MorphismConstructionInput[TargetMorphismValue, TargetDatum],
) -> None: ...


@overload
def retain_constructed_transport[
    SourceValue: CategoryPoint,
    SourceDatum,
    TargetValue: CategoryPoint,
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
    SourceElementValue: CategoryPoint,
    SourceMorphismValue: MorphismOfCategory,
    SourceDatum,
    TargetObjectValue: ObjectOfCategory,
    TargetElementValue: CategoryPoint,
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
    """Retain an ancestor input before the source initializer starts (specs/resolution.md, final decision 14).

    The key takes the role of the source; the retained input takes the role of the node
    it belongs to.  These differ where an object walk reaches ``(Mor(C), object)``, which
    *is* the node ``(C, morphism)`` and whose values retain a morphism input
    (POL-CAT-021).
    """
    if isinstance(source, ObjectConstructionInput):
        assert isinstance(construction, ObjectConstructionInput | MorphismConstructionInput)
        role = Role.OBJECT
    elif isinstance(source, ElementConstructionInput):
        assert isinstance(construction, ElementConstructionInput)
        role = Role.ELEMENT
    else:
        assert isinstance(construction, MorphismConstructionInput)
        role = Role.MORPHISM
    _retain_at_key(role, _construction_key(source), target, construction.canonical_image, construction)


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
    """Retain one result of ``method`` per receiver and argument sequence, arguments compared by identity.

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
