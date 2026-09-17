from _typeshed import Incomplete
from collections.abc import Callable
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict, cached_method as cached_method
from sage_categories.kernel.type_aliases import EqualityInput as EqualityInput
from typing import Any, Protocol, overload
type DiagramBox = Any

class NonstrictMonoidalModel[Object, Arrow]:

    def __init__(self, *, unit: Object, tensor_object: Callable[[Object, Object], Object], tensor_morphism: Callable[[Arrow, Arrow], Arrow], identity: Callable[[Object], Arrow], compose: Callable[[Arrow, Arrow], Arrow], inverse: Callable[[Arrow], Arrow], comparison: Callable[[tuple[Object, ...], tuple[Object, ...]], Arrow]) -> None:
        ...

    def wire(self, value: Object) -> Any:
        ...

    def box(self, name: str, domain: tuple[Object, ...], codomain: tuple[Object, ...], value: Arrow) -> DiagramBox:
        ...

    def evaluate(self, diagram: Any) -> Arrow:
        ...

class _PathArrow(Protocol):

    def domain(self) -> object:
        ...

    def codomain(self) -> object:
        ...

def evaluate_path(arrows: tuple[_PathArrow, ...], *, domain: object, codomain: object, identity: Callable[[object], object], compose: Callable[[object, object], object]) -> object:
    ...

class _ObjectValue:
    _model: NonstrictMonoidalModel
    model: Incomplete
    word: Incomplete
    value: Incomplete

    def __init__(self, word: tuple[object, ...]=(), value: object | None=None) -> None:
        ...

    @overload
    def __matmul__(self, other: _ObjectValue) -> _ObjectValue:
        ...

    @overload
    def __matmul__(self, other: _ArrowValue) -> _ArrowValue:
        ...
    __add__ = __matmul__

    def __eq__(self, other: EqualityInput) -> bool:
        ...

    def __hash__(self) -> int:
        ...

class _ArrowValue:
    _model: NonstrictMonoidalModel
    model: Incomplete
    dom: Incomplete
    cod: Incomplete
    value: Incomplete

    def __init__(self, dom: _ObjectValue, cod: _ObjectValue, value: object) -> None:
        ...

    @classmethod
    def id(cls, value: _ObjectValue) -> _ArrowValue:
        ...

    def __rshift__(self, other: _ArrowValue) -> _ArrowValue:
        ...

    def __matmul__(self, other: _ArrowValue | _ObjectValue) -> _ArrowValue:
        ...
    __add__ = __matmul__
