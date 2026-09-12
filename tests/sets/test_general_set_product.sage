"""The general Sets product exists independently of finite enumeration."""

from sympy import false, true

from sage_categories.cat.calculus import pair_maps
from sage_categories.cat.morphisms import Mor
from sage_categories.sets.finite import Sets


def test_general_set_product() -> None:
    left = Sets.from_membership(lambda value: true if value == "left" else false)
    right = Sets.from_membership(lambda value: true if value == "right" else false)
    product = Sets.Products()((left, right))

    point = product.point(("left", "right"))
    assert product.product_projection(0)(point).datum() == "left"
    assert product.product_projection(0)(point).parent() is left
    assert product.product_projection(1)(point).datum() == "right"
    assert product.product_projection(1)(point).parent() is right

    source = Sets.from_membership(lambda value: true if value == "source" else false)
    first = Mor(Sets)(source, left)(lambda _: "left")
    second = Mor(Sets)(source, right)(lambda _: "right")
    mediator = pair_maps(Sets, first, second)
    witness = source.point("source")

    assert mediator(witness).datum() == ("left", "right")
    assert mediator(witness).parent() is product
    assert (product.product_projection(0) * mediator)(witness).datum() == first(witness).datum()
    assert (product.product_projection(1) * mediator)(witness).datum() == second(witness).datum()


test_general_set_product()
