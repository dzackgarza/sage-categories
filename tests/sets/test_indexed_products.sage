from sympy import Q, pi, sqrt

from sage_categories.all import NN, Fun, Mor, Sets
from sage_categories.cat.cones import cocone, cocones, cone, cones
from sage_categories.cat.shapes import Discrete

integers = Sets.from_membership(lambda value: Q.integer(value))
natural_shape = Discrete(NN)
natural_diagram = Fun(natural_shape, Sets).from_object_rule(lambda vertex: integers)
natural_product = Sets.Limits(natural_shape)(natural_diagram)
natural_data = Sets.Limits(natural_shape).universal_data(natural_diagram)
family = natural_product.point(lambda index: index + 1)
assert natural_data.leg(101)(family).datum() == 102
source = integers
candidate = cone(
    natural_diagram,
    source,
    lambda vertex: Mor(Sets)(source, integers)(lambda value, vertex=vertex: value + vertex.point().datum()),
)
mediator = natural_data.lift(cones(natural_diagram)(candidate))
witness = source.point(5)
assert natural_data.leg(101)(mediator(witness)).datum() == 106

reals = Sets.from_membership(lambda value: Q.real(value))
real_shape = Discrete(reals)
real_diagram = Fun(real_shape, Sets).from_object_rule(lambda vertex: reals)
real_product = Sets.Limits(real_shape)(real_diagram)
real_data = Sets.Limits(real_shape).universal_data(real_diagram)
real_family = real_product.point(lambda index: index + 1)
assert real_data.leg(pi)(real_family).datum() == 1 + pi
real_candidate = cone(
    real_diagram,
    reals,
    lambda vertex: Mor(Sets)(reals, reals)(lambda value, vertex=vertex: value + vertex.point().datum()),
)
real_mediator = real_data.lift(cones(real_diagram)(real_candidate))
real_witness = reals.point(sqrt(2))
assert real_data.leg(pi)(real_mediator(real_witness)).datum() == pi + sqrt(2)


natural_coproduct = Sets.Colimits(natural_shape)(natural_diagram)
natural_coproduct_data = Sets.Colimits(natural_shape).universal_data(natural_diagram)
natural_injected = natural_coproduct_data.leg(101)(integers.point(5))
natural_cocandidate = cocone(
    natural_diagram,
    integers,
    lambda vertex: Mor(Sets)(integers, integers)(lambda value, vertex=vertex: value + vertex.point().datum()),
)
natural_descent = natural_coproduct_data.lift(cocones(natural_diagram)(natural_cocandidate))
assert natural_descent(natural_injected).datum() == 106
assert natural_descent(natural_coproduct.point((101, 5))).datum() == 106

real_coproduct = Sets.Colimits(real_shape)(real_diagram)
real_coproduct_data = Sets.Colimits(real_shape).universal_data(real_diagram)
real_injected = real_coproduct_data.leg(pi)(reals.point(sqrt(2)))
real_cocandidate = cocone(
    real_diagram,
    reals,
    lambda vertex: Mor(Sets)(reals, reals)(lambda value, vertex=vertex: value + vertex.point().datum()),
)
real_descent = real_coproduct_data.lift(cocones(real_diagram)(real_cocandidate))
assert real_descent(real_injected).datum() == pi + sqrt(2)
assert real_descent(real_coproduct.point((pi, sqrt(2)))).datum() == pi + sqrt(2)
