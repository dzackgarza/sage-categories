"""homotopy-core realization of the owned ``Mor`` tower.

Owned categories, objects, and morphisms remain the public identities.  This module
retains one private homotopy-core signature per exact owned category and lowers only
primitive owned arrows to native generators.  Identities, composites, and retained
inverses are constructed by homotopy-core itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import sage_categories_homotopy as homotopy

from sage_categories.cat.category import Category, composite_factors, is_composite
from sage_categories.cat.morphisms import MorphismCategory

__all__ = ["boundary", "dimension", "native_cell", "native_object", "native_signature", "retain_composite", "retain_generator", "retain_identity", "retain_inverses", "retain_whisker_left", "retain_whisker_right", "typecheck"]


@dataclass(slots=True)
class _CellState:
    owner: Category
    signature: homotopy.Signature
    objects: dict[int, tuple[object, homotopy.Cell]] = field(default_factory=dict)
    morphisms: dict[int, tuple[object, homotopy.Cell]] = field(default_factory=dict)


_states: dict[int, tuple[Category, _CellState]] = {}
_cell_owners: dict[int, tuple[object, Category]] = {}



def _cell_owner(value: object, proposed: Category) -> Category:
    identifier = id(value)
    match identifier in _cell_owners:
        case True:
            retained, owner = _cell_owners[identifier]
            assert retained is value
            return owner
        case False:
            _cell_owners[identifier] = (value, proposed)
            return proposed


def _root_owner(owner: Category) -> Category:
    from sage_categories.cat.morphisms import MorphismCategory

    root = owner
    while isinstance(root, MorphismCategory):
        root = root.base_category()
    return root


def _state(owner: Category) -> _CellState:
    owner = _root_owner(owner)
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
    from sage_categories.cat.morphisms import MorphismCategory

    match owner:
        case MorphismCategory():
            return native_cell(owner.base_category(), value)
        case Category():
            pass
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


def retain_identity(
    owner: Category,
    value: MorphismCategory.ObjectType,
) -> homotopy.Cell:
    """Retain ``value`` as the native identity on its exact owned source cell."""
    owner = _cell_owner(value, owner)
    state = _state(owner)
    cached = _cached_morphism(state, value)
    match cached is None:
        case False:
            return cached
        case True:
            source = native_object(owner, value.domain())
            target = native_object(owner, value.codomain())
            assert source.same_as(target), f"{value!r} is not an identity cell"
            return _retain_morphism(state, value, source.identity())


def retain_composite(
    owner: Category,
    value: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> homotopy.Cell:
    """Retain ``value = second * first`` via native top-boundary attachment."""
    owner = _cell_owner(value, owner)
    state = _state(owner)
    cached = _cached_morphism(state, value)
    first_native = native_cell(owner, first)
    second_native = native_cell(owner, second)
    native = first_native.attach(second_native, "target", [])
    match cached is None:
        case False:
            assert cached.same_as(native), (
                f"{value!r} is not the native top-boundary composite of its retained factors"
            )
            return cached
        case True:
            return _retain_morphism(state, value, native)


def _retain_lower_attachment(
    owner: Category,
    value: MorphismCategory.ObjectType,
    transformation: MorphismCategory.ObjectType,
    functor: MorphismCategory.ObjectType,
    side: Literal["source", "target"],
) -> homotopy.Cell:
    """Retain a whisker as homotopy-core attachment along the 0-dimensional boundary."""
    owner = _cell_owner(value, owner)
    state = _state(owner)
    transformation_native = native_cell(owner, transformation)
    functor_native = native_object(owner, functor)
    native = transformation_native.attach(functor_native, side, [])
    cached = _cached_morphism(state, value)
    match cached is None:
        case True:
            return _retain_morphism(state, value, native)
        case False:
            assert cached.same_as(native), f"{value!r} does not match its native whiskering attachment"
            return cached


def retain_whisker_left(
    owner: Category,
    value: MorphismCategory.ObjectType,
    functor: MorphismCategory.ObjectType,
    transformation: MorphismCategory.ObjectType,
) -> homotopy.Cell:
    """Retain ``functor . transformation`` by target-boundary attachment."""
    return _retain_lower_attachment(owner, value, transformation, functor, "target")


def retain_whisker_right(
    owner: Category,
    value: MorphismCategory.ObjectType,
    transformation: MorphismCategory.ObjectType,
    functor: MorphismCategory.ObjectType,
) -> homotopy.Cell:
    """Retain ``transformation . functor`` by source-boundary attachment."""
    return _retain_lower_attachment(owner, value, transformation, functor, "source")


def retain_generator(
    owner: Category,
    value: MorphismCategory.ObjectType,
    *,
    invertibility: Literal["directed", "invertible"] = "directed",
) -> homotopy.Cell:
    """Retain one primitive owned cell as a native signature generator."""
    owner = _cell_owner(value, owner)
    state = _state(owner)
    cached = _cached_morphism(state, value)
    match cached is None:
        case False:
            return cached
        case True:
            source = native_object(owner, value.domain())
            target = native_object(owner, value.codomain())
            native = state.signature.add_generator(source, target, invertibility=invertibility)
            return _retain_morphism(state, value, native)


def native_cell(owner: Category, value: MorphismCategory.ObjectType) -> homotopy.Cell:
    """Return the native cell for one exact owned arrow of ``owner``."""
    owner = _cell_owner(value, owner)
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
            return retain_identity(owner, value)
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
            retain_composite(owner, value, first, second)
        case False:
            classification: Literal["directed", "invertible"]
            match inverse is None:
                case True:
                    classification = "directed"
                case False:
                    classification = "invertible"
            retain_generator(owner, value, invertibility=classification)

    match inverse is None or inverse is value:
        case False:
            if _cached_morphism(state, inverse) is None:
                _retain_morphism(state, inverse, state.morphisms[id(value)][1].inverse())
        case True:
            pass
    return state.morphisms[id(value)][1]



def retain_inverses(
    owner: Category,
    forward: MorphismCategory.ObjectType,
    backward: MorphismCategory.ObjectType,
) -> None:
    """Synchronize an exact owned inverse pair with the native signature."""
    owner = _cell_owner(forward, owner)
    backward_owner = _cell_owner(backward, owner)
    assert backward_owner is owner
    state = _state(owner)
    forward_native = native_cell(owner, forward)
    match forward is backward:
        case True:
            return
        case False:
            pass
    try:
        state.signature.strengthen_invertibility(forward_native, invertibility="invertible")
    except ValueError as error:
        if "only generator cells" not in str(error):
            raise
    inverse_native = forward_native.inverse()
    state.signature.typecheck(inverse_native, True)
    backward_cached = _cached_morphism(state, backward)
    match backward_cached is None:
        case True:
            _retain_morphism(state, backward, inverse_native)
        case False:
            try:
                state.signature.strengthen_invertibility(
                    backward_cached, invertibility="invertible"
                )
            except ValueError as error:
                if "only generator cells" not in str(error):
                    raise
            state.signature.typecheck(backward_cached.inverse(), True)


def typecheck(owner: Category, value: MorphismCategory.ObjectType) -> None:
    owner = _cell_owner(value, owner)
    state = _state(owner)
    state.signature.typecheck(native_cell(owner, value), True)


def dimension(owner: Category, value: MorphismCategory.ObjectType) -> int:
    """Native dimension of one owned cell in the root signature."""
    owner = _cell_owner(value, owner)
    return native_cell(owner, value).dimension()


def boundary(
    owner: Category,
    value: MorphismCategory.ObjectType,
    side: Literal["source", "target"],
    depth: int = 0,
) -> object:
    """Reconstruct one exact owned boundary selected by homotopy-core.

    The native engine computes ``BoundaryPath(side, depth)``.  The owner/endpoints are
    retained public reconstruction data; traversing them chooses the exact owned value
    and the final assertion checks that it is the native boundary, rather than computing
    a second boundary representation in Python.
    """
    owner = _cell_owner(value, owner)
    from sage_categories.cat.morphisms import MorphismCategory

    assert depth >= 0
    native = native_cell(owner, value).boundary(side, depth)
    current_owner = owner
    current_value = value
    for level in range(depth + 1):
        match side:
            case "source":
                candidate = current_value.domain()
            case "target":
                candidate = current_value.codomain()
        match level == depth:
            case True:
                expected = native_object(current_owner, candidate)
                assert native.same_as(expected), (
                    f"native {side} boundary at depth {depth} does not reconstruct to "
                    f"the retained owned boundary {candidate!r}"
                )
                return candidate
            case False:
                assert isinstance(current_owner, MorphismCategory), (
                    f"{value!r} has no owned boundary at depth {depth}"
                )
                current_owner = current_owner.base_category()
                current_value = candidate
    raise AssertionError("unreachable boundary reconstruction")
