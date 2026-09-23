"""Bimodule maps retain the commuting-law owner and both action projections."""

import pytest

from sage_categories import Mor, ask
from sage_categories.cat.bimodules import Bimodules
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.monoidal import Cartesian
from sage_categories.cat.structured_objects import Monoids
from sage_categories.sets import Sets


def test_bimodule_morphisms_require_commuting_endpoints() -> None:
    structure = Cartesian(Sets)
    scalars = Sets((0, 1))
    square = binary_product_data(Sets, scalars, scalars).apex()
    monoid = Monoids(structure)(
        Mor(Sets)(square, scalars)(lambda pair: min(pair)),
        Mor(Sets)(structure.unit(), scalars)(lambda point: 1),
    )
    bimodules = Bimodules(monoid, monoid, structure)
    source, target = Sets((0, 1, 2)), Sets((10, 11, 12))
    left_domain = binary_product_data(Sets, scalars, source).apex()
    right_domain = binary_product_data(Sets, source, scalars).apex()
    left_action = Mor(Sets)(left_domain, source)(lambda pair: pair[0] * pair[1])
    noncommuting_right = Mor(Sets)(right_domain, source)(lambda pair: pair[1] * pair[0] + (1 - pair[1]))

    # Each action is unital and associative, but the two zero scalars act
    # by different constant maps. Their action pair is not a bimodule.
    pair = bimodules.ambient()((
        bimodules.left_modules()(left_action),
        bimodules.right_modules()(noncommuting_right),
        source,
    ))
    assert pair in bimodules.ambient()
    assert pair not in bimodules
    with pytest.raises(AssertionError):
        bimodules(left_action, noncommuting_right)
    with pytest.raises(AssertionError):
        bimodules.homomorphism(pair, pair, Mor(Sets)(source, source).one())

    # Zero acts by the constant zero on the left and by parity on the right.
    # These distinct idempotents commute. Translation gives a nonidentity map
    # to a different carrier, preserving both actions.
    right_action = Mor(Sets)(right_domain, source)(
        lambda pair: pair[1] * pair[0] + (1 - pair[1]) * (pair[0] % 2)
    )
    module = bimodules(left_action, right_action)
    forward = Mor(Sets)(source, target)(lambda value: value + 10)
    backward = Mor(Sets)(target, source)(lambda value: value - 10)
    Sets.retain_inverses(forward, backward)
    left = bimodules.left_modules().transport(bimodules.to_left().on_object(module), forward)
    right = bimodules.right_modules().transport(bimodules.to_right().on_object(module), forward)
    translated = bimodules(left.action(), right.action())

    arrow = bimodules.homomorphism(module, translated, forward)
    inverse = bimodules.homomorphism(translated, module, backward)
    assert arrow in Mor(bimodules)(module, translated)
    assert arrow.domain() is module
    assert arrow.codomain() is translated
    assert bimodules.forgetful().on_morphism(arrow) is forward
    for projection, modules in (
        (bimodules.to_left(), bimodules.left_modules()),
        (bimodules.to_right(), bimodules.right_modules()),
    ):
        image = projection.on_morphism(arrow)
        assert image in Mor(modules)(projection.on_object(module), projection.on_object(translated))
        assert modules.forgetful().on_morphism(image) is forward
    assert module.left_action()(left_domain.point((0, 1))).datum() == 0
    assert module.right_action()(right_domain.point((1, 0))).datum() == 1
    assert bimodules.forgetful().on_morphism(arrow)(source.point(1)).datum() == 11
    assert ask(inverse * arrow == Mor(bimodules)(module, module).one()) is True
    assert ask(arrow * inverse == Mor(bimodules)(translated, translated).one()) is True


test_bimodule_morphisms_require_commuting_endpoints()
