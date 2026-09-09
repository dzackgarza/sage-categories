from __future__ import annotations

from sympy import Q

from sage_categories import omega
from sage_categories.all import Fun, Mor, Sets, Unknown, ask
from sage_categories.cat.cones import cocone, cocones

integers = Sets.from_membership(lambda value: Q.integer(value))


def stage(vertex):
    return vertex.point().datum()


def transition(arrow):
    offset = stage(arrow.codomain()) - stage(arrow.domain())
    return Mor(Sets)(integers, integers)(lambda value, offset=offset: value + offset)


diagram = Fun(omega, Sets)(lambda vertex: integers, transition)
colimit = Sets.Colimits(omega)(diagram)
data = Sets.Colimits(omega).universal_data(diagram)

at_two = data.leg(2)(integers.point(5))
at_101 = data.leg(101)(integers.point(104))
assert ask(at_two == at_101) is True
assert ask(colimit.point((2, 5)) == colimit.point((101, 104))) is True
assert ask(colimit.point((2, 5)) == colimit.point((5, 9))) is Unknown

candidate = cocone(
    diagram,
    integers,
    lambda vertex: Mor(Sets)(integers, integers)(
        lambda value, vertex=vertex: value - stage(vertex)
    ),
)
descent = data.lift(cocones(diagram)(candidate))
assert descent(at_two).datum() == 3
assert descent(at_101).datum() == 3
assert (descent * data.leg(101))(integers.point(104)).datum() == 3
