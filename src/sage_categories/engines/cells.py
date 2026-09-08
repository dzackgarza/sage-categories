"""homotopy-core realization of the owned ``Mor`` tower.

Owned categories, objects, and morphisms remain the public identities.  This module
retains one private homotopy-core signature per exact owned category and lowers only
primitive owned arrows to native generators.  Identities, composites, and retained
inverses are constructed by homotopy-core itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import sage_categories_homotopy as homotopy

from sage_categories.cat.category import Category, composite_factors, is_composite
from sage_categories.cat.morphisms import MorphismCategory

__all__ = ["native_cell", "native_object", "native_signature", "typecheck"]


@dataclass(slots=True)
class _CellState:
    owner: Category
    signature: homotopy.Signature
    objects: dict[int, tuple[object, homotopy.Cell]] = field(default_factory=dict)
    morphisms: dict[int, tuple[object, homotopy.Cell]] = field(default_factory=dict)


_states: dict[int, tuple[Category, _CellState]] = {}


def _state(owner: Category) -> _CellState:
    identifier = id(owner)
    match identifier in _states:
        case True:
            retained, state = _states[identifier]
            assert retained is owner
            return state
        case False:
            state = _CellState(owner, homotopy.Signature())
            _states[identifier] = (owner, state)
            return state


def native_signature(owner: Category) -> homotopy.Signature:
    return _state(owner).signature


def native_object(owner: Category, value: object) -> homotopy.Cell:
    state = _state(owner)
    identifier = id(value)
    match identifier in state.objects:
        case True:
            retained, native = state.objects[identifier]
            assert retained is value
            return native
        case False:
            assert value in owner, f"{value!r} is not an object of {owner!r}"
            native = state.signature.add_object()
            state.objects[identifier] = (value, native)
            return native


def _retain_morphism(state: _CellState, value: MorphismCategory.ObjectType, native: homotopy.Cell) -> homotopy.Cell:
    state.signature.typecheck(native, True)
    state.morphisms[id(value)] = (value, native)
    return native


def _cached_morphism(state: _CellState, value: MorphismCategory.ObjectType) -> homotopy.Cell | None:
    identifier = id(value)
    match identifier in state.morphisms:
        case True:
            retained, native = state.morphisms[identifier]
            assert retained is value
            return native
        case False:
            return None


def native_cell(owner: Category, value: MorphismCategory.ObjectType) -> homotopy.Cell:
    """Return the native cell for one exact owned arrow of ``owner``."""
    state = _state(owner)
    cached = _cached_morphism(state, value)
    match cached is None:
        case False:
            return cached
        case True:
            pass
    assert value in owner.morphism_category(1), f"{value!r} is not a morphism of {owner!r}"

    identity = owner.morphism_category(1)(value.domain(), value.domain()).one()
    match identity is value:
        case True:
            return _retain_morphism(state, value, native_object(owner, value.domain()).identity())
        case False:
            pass

    inverse = owner.retained_inverse(value)
    match inverse is None or inverse is value:
        case False:
            inverse_native = _cached_morphism(state, inverse)
            match inverse_native is None:
                case False:
                    return _retain_morphism(state, value, inverse_native.inverse())
                case True:
                    pass
        case True:
            pass

    match is_composite(value):
        case True:
            first, second = composite_factors(value)
            first_native = native_cell(owner, first)
            second_native = native_cell(owner, second)
            embeddings = first_native.target().embeddings(second_native.source())
            assert embeddings, "composable owned arrows have no native boundary embedding"
            native = first_native.attach(second_native, "target", embeddings[0])
            _retain_morphism(state, value, native)
        case False:
            source = native_object(owner, value.domain())
            target = native_object(owner, value.codomain())
            classification = "invertible" if inverse is not None else "directed"
            native = state.signature.add_generator(source, target, invertibility=classification)
            _retain_morphism(state, value, native)

    match inverse is None or inverse is value:
        case False:
            if _cached_morphism(state, inverse) is None:
                _retain_morphism(state, inverse, state.morphisms[id(value)][1].inverse())
        case True:
            pass
    return state.morphisms[id(value)][1]


def typecheck(owner: Category, value: MorphismCategory.ObjectType) -> None:
    state = _state(owner)
    state.signature.typecheck(native_cell(owner, value), True)
