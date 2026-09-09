"""Cartesian finite-set coherence comparisons are reconstructed from CAP."""

from sympy import Q

from sage_categories.all import Cartesian, Sets, ask
from sage_categories.sets._finite_cap import finite_native_morphism

structure = Cartesian(Sets)
X, Y, Z = (Sets(values) for values in ((0, 1), (2, 3), (4, 5)))
triples = structure.associator().domain().domain()
alpha = structure.associator().component(triples((X, Y, Z)))
assert finite_native_morphism(alpha).native is not None
assert alpha(alpha.domain().point(((1, 2), 5))).datum() == (1, (2, 5))
assert alpha.inverse()(alpha(alpha.domain().point(((1, 2), 5)))).datum() == ((1, 2), 5)

left = structure.left_unitor().component(X)
right = structure.right_unitor().component(X)
assert finite_native_morphism(left).native is not None
assert finite_native_morphism(right).native is not None
assert left(left.domain().point(((), 1))).datum() == 1
assert right(right.domain().point((1, ()))).datum() == 1
assert left.inverse()(X.point(1)).datum() == ((), 1)
assert right.inverse()(X.point(1)).datum() == (1, ())
assert ask(structure.pentagon(X, X, Y, Z)) is True
assert ask(structure.triangle(X, Y)) is True


# The native CAP realization is finite-domain only.  A rule-defined set keeps the
# same public Cartesian coherence through the generic selected-product calculus,
# without acquiring or requiring a finite enumeration.
integers = Sets.from_membership(lambda value: Q.integer(value))
represented_triples = structure.associator().domain().domain()
represented_alpha = structure.associator().component(
    represented_triples((integers, integers, integers))
)
represented_point = represented_alpha.domain().point(((1, 2), 3))
assert represented_alpha(represented_point).datum() == (1, (2, 3))
assert represented_alpha.inverse()(represented_alpha(represented_point)).datum() == ((1, 2), 3)
represented_left = structure.left_unitor().component(integers)
represented_right = structure.right_unitor().component(integers)
assert represented_left(represented_left.domain().point(((), 7))).datum() == 7
assert represented_right(represented_right.domain().point((7, ()))).datum() == 7
assert represented_left.inverse()(integers.point(7)).datum() == ((), 7)
assert represented_right.inverse()(integers.point(7)).datum() == (7, ())
assert ask(structure.pentagon(integers, integers, integers, integers)) is True
assert ask(structure.triangle(integers, integers)) is True
