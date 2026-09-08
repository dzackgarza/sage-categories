"""Cartesian finite-set coherence comparisons are reconstructed from CAP."""

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
