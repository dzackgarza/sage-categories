"""Represented finite topologies and continuous maps with retained inverse image on opens."""

from sage_categories.all import Mor, Sets, ask
from sage_categories.geometry import TopologicalSpaces


def test_continuous_map_retains_inverse_image_functor_and_composition() -> None:
    spaces = TopologicalSpaces()
    three = Sets((0, 1, 2))
    sierpinski = spaces(
        three,
        (
            frozenset(),
            frozenset((2,)),
            frozenset((1, 2)),
            frozenset((0, 1, 2)),
        ),
    )
    two = Sets((0, 1))
    target = spaces(two, (frozenset(), frozenset((1,)), frozenset((0, 1))))
    collapse = Mor(spaces)(sierpinski, target)(Mor(Sets)(three, two)(lambda value: int(value > 0)))
    inverse = collapse.inverse_image()
    target_open = target.open_object(frozenset((1,)))
    source_open = inverse.on_object(target_open)
    assert source_open.point().datum() == frozenset((1, 2))
    assert inverse.domain() is target.open_category() and inverse.codomain() is sierpinski.open_category()

    one = Sets((0,))
    terminal = spaces(one, (frozenset(), frozenset((0,))))
    constant = Mor(spaces)(target, terminal)(Mor(Sets)(two, one)(lambda _: 0))
    composite = constant * collapse
    full = terminal.open_object(frozenset((0,)))
    assert composite.inverse_image().on_object(full).point().datum() == frozenset((0, 1, 2))
    iterated = collapse.inverse_image().on_object(constant.inverse_image().on_object(full))
    assert ask(composite.inverse_image().on_object(full) == iterated) is True


test_continuous_map_retains_inverse_image_functor_and_composition()
