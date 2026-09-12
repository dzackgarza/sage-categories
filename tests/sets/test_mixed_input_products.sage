"""Enumerated, rule-defined, and represented factors share one Sets product."""

from sympy import Q, sqrt

from sage_categories.cat.morphisms import Mor
from sage_categories.cat.predicates import ask
from sage_categories.sets.finite import Sets


def test_mixed_input_product() -> None:
    enumerated = Sets((10, 20))
    integers = Sets.from_membership(lambda value: Q.integer(value))
    reals = Sets.from_membership(lambda value: Q.real(value))
    product = Sets.Products()((enumerated, integers, reals))

    point = product.point((10, 9, sqrt(2)))
    assert ask(product.membership_proposition(point)) is True
    assert product.product_projection(0)(point).datum() == 10
    assert product.product_projection(0)(point).parent() is enumerated
    assert product.product_projection(1)(point).datum() == 9
    assert product.product_projection(1)(point).parent() is integers
    assert product.product_projection(2)(point).datum() == sqrt(2)
    assert product.product_projection(2)(point).parent() is reals

    total = Mor(Sets)(product, reals)(lambda components: components[0] + components[1] + components[2])
    assert total(point).datum() == 19 + sqrt(2)
    assert total(point).parent() is reals


test_mixed_input_product()
