"""DisCoPy evaluates tensor diagrams through retained nonstrict comparisons."""

from dataclasses import dataclass

from sage_categories.engines.diagrams import NonstrictMonoidalModel


@dataclass(frozen=True)
class Arrow:
    domain: tuple[str, ...]
    codomain: tuple[str, ...]
    weight: int


def identity(value):
    return Arrow(value, value, 0)


def compose(second, first):
    assert first.codomain == second.domain
    return Arrow(first.domain, second.codomain, first.weight + second.weight)


def inverse(value):
    return Arrow(value.codomain, value.domain, -value.weight)


def tensor_object(first, second):
    return first + second


def tensor_morphism(first, second):
    return Arrow(
        first.domain + second.domain,
        first.codomain + second.codomain,
        first.weight + second.weight,
    )


def interpret_word(word):
    return tuple(entry for atom in word for entry in atom)


def comparison(first_word, second_word):
    source = interpret_word(first_word + second_word)
    target = tensor_object(interpret_word(first_word), interpret_word(second_word))
    return Arrow(source, target, 10 * len(first_word) + len(second_word))


def test_nonstrict_tensor_uses_comparison_maps() -> None:
    model = NonstrictMonoidalModel(
        unit=(),
        tensor_object=tensor_object,
        tensor_morphism=tensor_morphism,
        identity=identity,
        compose=compose,
        inverse=inverse,
        comparison=comparison,
    )
    f = model.box("f", (("x",),), (("y",), ("z",)), Arrow(("x",), ("y", "z"), 1))
    g = model.box("g", (("u",),), (("v",),), Arrow(("u",), ("v",), 2))
    result = model.evaluate(f @ g)
    assert result.domain == ("x", "u")
    assert result.codomain == ("y", "z", "v")
    # DisCoPy evaluates the tensor layer through left/right identity contexts; every
    # parallel composition is conjugated by the retained nonstrict comparisons.
    assert result.weight == -8


test_nonstrict_tensor_uses_comparison_maps()
