"""Represented real factors retain their full Sets product semantics."""

from sympy import Dummy, Lambda, Q, pi, sqrt

from sage_categories.cat.calculus import pair_maps
from sage_categories.cat.morphisms import Mor
from sage_categories.sets.finite import Sets


def test_represented_real_product() -> None:
    reals = Sets.from_membership(lambda value: Q.real(value))
    product = Sets.Products()((reals, reals))

    point = product.point((sqrt(2), pi))
    assert product.product_projection(0)(point).datum() == sqrt(2)
    assert product.product_projection(0)(point).parent() is reals
    assert product.product_projection(1)(point).datum() == pi
    assert product.product_projection(1)(point).parent() is reals

    variable = Dummy("x")
    double = Mor(Sets)(reals, reals)(Lambda((variable,), 2r * variable))
    translate = Mor(Sets)(reals, reals)(Lambda((variable,), variable + 1))
    mediator = pair_maps(Sets, double, translate)
    witness = reals.point(sqrt(2))

    assert double(witness).datum() == 2 * sqrt(2)
    assert translate(witness).datum() == 1 + sqrt(2)
    assert mediator(witness).datum() == (2 * sqrt(2), 1 + sqrt(2))
    assert mediator(witness).parent() is product
    assert (product.product_projection(0) * mediator)(witness).datum() == double(witness).datum()
    assert (product.product_projection(1) * mediator)(witness).datum() == translate(witness).datum()


test_represented_real_product()
