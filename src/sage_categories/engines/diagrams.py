"""DisCoPy interpretation into supplied owned nonstrict monoidal structures.

DisCoPy owns formal string-diagram composition, tensoring, and interchange.  This
module supplies its semantic codomain: objects retain a chosen interpretation of a
wire word, and arrows retain an owned semantic morphism.  Tensoring arrows applies
the supplied comparison maps ``E(uv) -> E(u) tensor E(v)``; no Python traversal of a
DisCoPy diagram evaluates boxes or layers.
"""

from __future__ import annotations

from collections.abc import Callable

from discopy import cat as discopy_cat
from discopy import monoidal as discopy_monoidal

__all__ = ["NonstrictMonoidalModel", "evaluate_path"]


class _ObjectValue:
    _model: NonstrictMonoidalModel

    def __init__(self, word: tuple[object, ...] = (), value: object | None = None) -> None:
        self.model = type(self)._model
        self.word = word
        self.value = self.model._unit if value is None and not word else value

    def __matmul__(self, other: _ObjectValue | _ArrowValue) -> _ObjectValue | _ArrowValue:
        assert self.model is other.model
        if isinstance(other, _ArrowValue):
            return type(other).id(self) @ other
        return self.model._word(self.word + other.word)

    __add__ = __matmul__

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, _ObjectValue)
            and self.model is other.model
            and len(self.word) == len(other.word)
            and all(first is second for first, second in zip(self.word, other.word, strict=True))
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
        return type(self)(self.dom, other.cod, self.model._compose(other.value, self.value))

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


class NonstrictMonoidalModel:
    """A DisCoPy semantic target for one supplied owned monoidal structure."""

    def __init__(
        self,
        *,
        unit: object,
        tensor_object: Callable[[object, object], object],
        tensor_morphism: Callable[[object, object], object],
        identity: Callable[[object], object],
        compose: Callable[[object, object], object],
        inverse: Callable[[object], object],
        comparison: Callable[[tuple[object, ...], tuple[object, ...]], object],
    ) -> None:
        self._unit = unit
        self._tensor_object = tensor_object
        self._tensor_morphism = tensor_morphism
        self._identity = identity
        self._compose = compose
        self._inverse = inverse
        self._comparison = comparison
        self._word_cache: dict[tuple[int, ...], _ObjectValue] = {}
        self._wire_values: dict[str, object] = {}
        self._wire_tokens: dict[int, tuple[object, str]] = {}
        self._next_wire = 0
        self._object_type = type(
            f"_NonstrictObject_{id(self)}", (_ObjectValue,), {"_model": self}
        )
        self._arrow_type = type(
            f"_NonstrictArrow_{id(self)}", (_ArrowValue,), {"_model": self}
        )
        self._category = discopy_cat.Category(self._object_type, self._arrow_type)

    def _word(self, word: tuple[object, ...]) -> _ObjectValue:
        key = tuple(id(value) for value in word)
        if key not in self._word_cache:
            match word:
                case ():
                    value = self._unit
                case (first, *rest):
                    value = first
                    for following in rest:
                        value = self._tensor_object(value, following)
            self._word_cache[key] = self._object_type(word, value)
        return self._word_cache[key]

    def wire(self, value: object) -> discopy_monoidal.Ty:
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
        return discopy_monoidal.Ty(token)

    def box(
        self,
        name: str,
        domain: tuple[object, ...],
        codomain: tuple[object, ...],
        value: object,
    ) -> discopy_monoidal.Box:
        """A DisCoPy generating box retaining one exact owned semantic morphism."""
        dom = discopy_monoidal.Ty(*(self.wire(item).inside[0] for item in domain))
        cod = discopy_monoidal.Ty(*(self.wire(item).inside[0] for item in codomain))
        return discopy_monoidal.Box(name, dom, cod, data=value)

    def evaluate(self, diagram: discopy_monoidal.Diagram) -> object:
        """Interpret ``diagram`` entirely through DisCoPy's monoidal functor evaluator."""
        def object_image(atom: object) -> _ObjectValue:
            value = self._wire_values[str(atom)]
            return self._word((value,))

        def arrow_image(box: discopy_monoidal.Box) -> _ArrowValue:
            dom_word = tuple(self._wire_values[str(atom)] for atom in box.dom.inside)
            cod_word = tuple(self._wire_values[str(atom)] for atom in box.cod.inside)
            return self._arrow_type(self._word(dom_word), self._word(cod_word), box.data)

        functor = discopy_monoidal.Functor(
            object_image,
            arrow_image,
            cod=self._category,
        )
        return functor(diagram).value


def evaluate_path(
    arrows: tuple[object, ...],
    *,
    domain: object,
    codomain: object,
    identity: Callable[[object], object],
    compose: Callable[[object, object], object],
) -> object:
    """Compose a retained semantic path through DisCoPy's native arrow evaluator."""
    object_type = type(
        f"_PathObject_{id(arrows)}",
        (),
        {
            "__init__": lambda self, value=None: setattr(self, "value", value),
            "__eq__": lambda self, other: type(self) is type(other) and self.value is other.value,
            "__hash__": lambda self: hash(id(self.value)),
        },
    )

    class ArrowValue:
        def __init__(self, dom, cod, value):
            self.dom, self.cod, self.value = dom, cod, value

        @classmethod
        def id(cls, value):
            return cls(value, value, identity(value.value))

        def __rshift__(self, other):
            assert self.cod == other.dom
            return type(self)(self.dom, other.cod, compose(other.value, self.value))

    category = discopy_cat.Category(object_type, ArrowValue)
    objects: dict[int, object] = {}

    def ob(value: object):
        key=id(value)
        if key not in objects:
            objects[key]=object_type(value)
        return objects[key]

    boxes=[]
    current=domain
    for index, arrow in enumerate(arrows):
        target = arrow.codomain()
        boxes.append(discopy_cat.Box(f"a{index}", discopy_cat.Ob(str(id(current))), discopy_cat.Ob(str(id(target))), data=arrow))
        current=target
    assert current is codomain
    token_values={str(id(value)): value for value in [domain, codomain, *(a.domain() for a in arrows), *(a.codomain() for a in arrows)]}
    functor=discopy_cat.Functor(
        lambda token: ob(token_values[token.name]),
        lambda box: ArrowValue(ob(box.data.domain()), ob(box.data.codomain()), box.data),
        cod=category,
    )
    if not boxes:
        return identity(domain)
    diagram=boxes[0]
    for box in boxes[1:]:
        diagram = diagram >> box
    return functor(diagram).value
