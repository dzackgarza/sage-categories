"""Represented quotients preserve non-enumerated carriers and exact class equality."""

from sympy import Q, false, true

from sage_categories.all import Sets, Unknown, ask


def test_non_enumerated_quotient_uses_owned_equivalence_relation() -> None:
    integers = Sets.from_membership(lambda value: Q.integer(value))

    def same_parity(left, right):
        match bool((left.datum() - right.datum()) % 2):
            case False:
                return true
            case True:
                return false

    quotient, projection = Sets.quotient(integers, same_parity)
    assert Sets.finite_points(quotient) is Unknown

    even = projection(integers.point(2))
    even_again = projection(integers.point(4))
    odd = projection(integers.point(3))
    assert ask(even == even_again) is True
    assert ask(even == odd) is False

    direct = quotient.point(6)
    assert ask(direct == even) is True
    assert Sets.quotient_representative(even).datum() == 2
    assert Sets.quotient_representative(direct).datum() == 6
    assert projection.domain() is integers
    assert projection.codomain() is quotient


test_non_enumerated_quotient_uses_owned_equivalence_relation()
