"""DisCoPy interpretation into supplied owned nonstrict monoidal structures.

DisCoPy owns formal string-diagram composition, tensoring, and interchange.  This
module supplies its semantic codomain: objects retain a chosen interpretation of a
wire word, and arrows retain an owned semantic morphism.  Tensoring arrows applies
the supplied comparison maps ``E(uv) -> E(u) tensor E(v)``; no Python traversal of a
DisCoPy diagram evaluates boxes or layers.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import cache
from importlib import import_module
from typing import Any, Protocol, cast, overload

from sage_categories.kernel.type_aliases import EqualityInput


@cache
def _discopy_cat() -> Any:
    return import_module("discopy.cat")


@cache
def _discopy_monoidal() -> Any:
    return import_module("discopy.monoidal")

__all__ = ["DiagramBox", "NonstrictMonoidalModel", "evaluate_path"]

type DiagramBox = Any


class _ObjectValue:
    _model: NonstrictMonoidalModel

    def __init__(
        self, word: tuple[object, ...] = (), value: object | None = None
    ) -> None:
        self.model = type(self)._model
        self.word = word
        self.value = self.model._unit if value is None and not word else value

    @overload
    def __matmul__(self, other: _ObjectValue) -> _ObjectValue: ...

    @overload
    def __matmul__(self, other: _ArrowValue) -> _ArrowValue: ...

    def __matmul__(
        self, other: _ObjectValue | _ArrowValue
    ) -> _ObjectValue | _ArrowValue:
        assert self.model is other.model
        if isinstance(other, _ArrowValue):
            return type(other).id(self) @ other
        return self.model._word(self.word + other.word)

    __add__ = __matmul__

    def __eq__(self, other: EqualityInput) -> bool:
        return (
            isinstance(other, _ObjectValue)
            and self.model is other.model
            and len(self.word) == len(other.word)
            and all(
                first is second
                for first, second in zip(self.word, other.word, strict=True)
            )
        )

    def __hash__(self) -> int:
        return hash((id(self.model), *(id(value) for value in self.word)))


class _ArrowValue:
    _model: NonstrictMonoidalModel

    def __init__(self, dom: _ObjectValue, cod: _ObjectValue, value: object) -> None:
        self.model = type(self)._model
        self.dom = dom
        self.cod = cod
        self.value = value

    @classmethod
    def id(cls, value: _ObjectValue) -> _ArrowValue:
        return cls(value, value, cls._model._identity(value.value))

    def __rshift__(self, other: _ArrowValue) -> _ArrowValue:
        assert self.model is other.model and self.cod == other.dom
        return type(self)(
            self.dom, other.cod, self.model._compose(other.value, self.value)
        )

    def __matmul__(self, other: _ArrowValue | _ObjectValue) -> _ArrowValue:
        assert self.model is other.model
        if isinstance(other, _ObjectValue):
            return self @ type(self).id(other)
        model = self.model
        dom, cod = self.dom @ other.dom, self.cod @ other.cod
        raw = model._tensor_morphism(self.value, other.value)
        comparison_dom = model._comparison(self.dom.word, other.dom.word)
        comparison_cod = model._comparison(self.cod.word, other.cod.word)
        semantic = model._compose(
            model._inverse(comparison_cod),
            model._compose(raw, comparison_dom),
        )
        return type(self)(dom, cod, semantic)

    __add__ = __matmul__


class NonstrictMonoidalModel[Object, Arrow]:
    """A DisCoPy semantic target for one supplied owned monoidal structure."""

    def __init__(
        self,
        *,
        unit: Object,
        tensor_object: Callable[[Object, Object], Object],
        tensor_morphism: Callable[[Arrow, Arrow], Arrow],
        identity: Callable[[Object], Arrow],
        compose: Callable[[Arrow, Arrow], Arrow],
        inverse: Callable[[Arrow], Arrow],
        comparison: Callable[[tuple[Object, ...], tuple[Object, ...]], Arrow],
    ) -> None:
        self._unit = unit
        self._tensor_object = tensor_object
        self._tensor_morphism = tensor_morphism
        self._identity = identity
        self._compose = compose
        self._inverse = inverse
        self._comparison = comparison
        self._word_cache: dict[tuple[int, ...], _ObjectValue] = {}
        self._wire_values: dict[str, Object] = {}
        self._wire_tokens: dict[int, tuple[Object, str]] = {}
        self._next_wire = 0
        self._object_type: type[_ObjectValue] = type(
            f"_NonstrictObject_{id(self)}",
            (_ObjectValue,),
            {"_model": self},
        )
        self._arrow_type: type[_ArrowValue] = type(
            f"_NonstrictArrow_{id(self)}",
            (_ArrowValue,),
            {"_model": self},
        )
        self._category = _discopy_cat().Category(self._object_type, self._arrow_type)

    def _word(self, word: tuple[Object, ...]) -> _ObjectValue:
        key = tuple(id(value) for value in word)
        if key not in self._word_cache:
            match len(word):
                case 0:
                    value = self._unit
                case _:
                    value = word[0]
                    for following in word[1:]:
                        value = self._tensor_object(value, following)
            self._word_cache[key] = self._object_type(word, value)
        return self._word_cache[key]

    def wire(self, value: Object) -> Any:
        """A stable DisCoPy atomic wire retaining one exact owned object."""
        identifier = id(value)
        if identifier in self._wire_tokens:
            retained, token = self._wire_tokens[identifier]
            assert retained is value
        else:
            token = f"w{self._next_wire}"
            self._next_wire += 1
            self._wire_tokens[identifier] = (value, token)
            self._wire_values[token] = value
        return _discopy_monoidal().Ty(token)

    def box(
        self,
        name: str,
        domain: tuple[Object, ...],
        codomain: tuple[Object, ...],
        value: Arrow,
    ) -> DiagramBox:
        """A DisCoPy generating box retaining one exact owned semantic morphism."""
        monoidal = _discopy_monoidal()
        dom = monoidal.Ty(*(self.wire(item).inside[0] for item in domain))
        cod = monoidal.Ty(*(self.wire(item).inside[0] for item in codomain))
        return monoidal.Box(name, dom, cod, data=value)

    def evaluate(self, diagram: Any) -> Arrow:
        """Interpret ``diagram`` entirely through DisCoPy's monoidal functor evaluator."""

        def object_image(atom: object) -> _ObjectValue:
            value = self._wire_values[str(atom)]
            return self._word((value,))

        def arrow_image(box: Any) -> _ArrowValue:
            dom_word = tuple(self._wire_values[str(atom)] for atom in box.dom.inside)
            cod_word = tuple(self._wire_values[str(atom)] for atom in box.cod.inside)
            return self._arrow_type(
                self._word(dom_word), self._word(cod_word), box.data
            )

        functor = _discopy_monoidal().Functor(
            object_image,
            arrow_image,
            cod=self._category,
        )
        return cast(Arrow, functor(diagram).value)


class _PathArrow(Protocol):
    def domain(self) -> object: ...

    def codomain(self) -> object: ...


def evaluate_path(
    arrows: tuple[_PathArrow, ...],
    *,
    domain: object,
    codomain: object,
    identity: Callable[[object], object],
    compose: Callable[[object, object], object],
) -> object:
    """Compose a retained semantic path through DisCoPy's native arrow evaluator."""

    class ObjectValue:
        def __init__(self, value: object) -> None:
            self.value = value

        def __eq__(self, other: EqualityInput) -> bool:
            return isinstance(other, ObjectValue) and self.value is other.value

        def __hash__(self) -> int:
            return hash(id(self.value))

    class ArrowValue:
        def __init__(self, dom: ObjectValue, cod: ObjectValue, value: object) -> None:
            self.dom, self.cod, self.value = dom, cod, value

        @classmethod
        def id(cls, value: ObjectValue) -> ArrowValue:
            return cls(value, value, identity(value.value))

        def __rshift__(self, other: ArrowValue) -> ArrowValue:
            assert self.cod == other.dom
            return type(self)(self.dom, other.cod, compose(other.value, self.value))

    cat = _discopy_cat()
    category = cat.Category(ObjectValue, ArrowValue)
    objects: dict[int, ObjectValue] = {}

    def ob(value: object) -> ObjectValue:
        key = id(value)
        if key not in objects:
            objects[key] = ObjectValue(value)
        return objects[key]

    boxes = []
    current = domain
    for index, arrow in enumerate(arrows):
        target = arrow.codomain()
        boxes.append(
            cat.Box(
                f"a{index}",
                cat.Ob(str(id(current))),
                cat.Ob(str(id(target))),
                data=arrow,
            )
        )
        current = target
    assert current is codomain
    token_values = {
        str(id(value)): value
        for value in [
            domain,
            codomain,
            *(a.domain() for a in arrows),
            *(a.codomain() for a in arrows),
        ]
    }
    functor = cat.Functor(
        lambda token: ob(token_values[token.name]),
        lambda box: ArrowValue(
            ob(box.data.domain()), ob(box.data.codomain()), box.data
        ),
        cod=category,
    )
    if not boxes:
        return identity(domain)
    diagram = boxes[0]
    for box in boxes[1:]:
        diagram = diagram >> box
    return cast(object, functor(diagram).value)
