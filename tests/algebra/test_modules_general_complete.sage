"""The unified module API stays scalar-general through free modules and presentations."""

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ

from sage_categories.algebra.abelian import (
    AbelianTensor,
    abelian_homomorphism,
    integer_group,
    presented_abelian_group,
    tensor_mediator,
)
from sage_categories.algebra.modules import (
    finite_free_matrix_morphism,
    finitely_presented_module,
    ordinary_modules,
    presented_module_factor,
    presented_module_projection,
    presented_module_relation,
    presented_module_zero,
)
from sage_categories.cat.category import ask
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import Monoids


def matrix_ring():
    """``M_2(F_2)`` as a noncommutative scalar monoid in ``(Ab, tensor)``."""
    engine = AdditiveAbelianGroup([2, 2, 2, 2])
    entries = lambda datum: [int(coefficient) for coefficient in datum.vector()]
    element = lambda values: engine.linear_combination_of_smith_form_gens(vector(ZZ, values))

    def multiply(first, second):
        x, y = entries(first), entries(second)
        return element(
            [
                x[0] * y[0] + x[1] * y[2],
                x[0] * y[1] + x[1] * y[3],
                x[2] * y[0] + x[3] * y[2],
                x[2] * y[1] + x[3] * y[3],
            ]
        )

    group = presented_abelian_group(engine)
    one = element([1, 0, 0, 1])
    ring = Monoids(AbelianTensor())(
        tensor_mediator(group, group, group, multiply),
        abelian_homomorphism(integer_group(), group, lambda coefficient: coefficient * one),
    )
    return element, group, ring


def test_unified_module_api_preserves_noncommutative_scalars_and_universal_factor() -> None:
    element, group, ring = matrix_ring()
    modules = ordinary_modules(ring)
    e11 = group.point(element([1, 0, 0, 0]))
    e12 = element([0, 1, 0, 0])
    e21 = element([0, 0, 1, 0])
    e22 = group.point(element([0, 0, 0, 1]))

    quotient = finitely_presented_module(modules, ((e11,),))
    relation = presented_module_relation(modules, quotient)
    zero = presented_module_zero(modules, quotient)
    projection = presented_module_projection(modules, quotient)
    line = relation.codomain()

    # The public facade keeps the exact supplied noncommutative scalar owner.
    assert quotient in modules
    assert modules.scalars() is ring
    assert ring is not None
    assert relation in Mor(modules)(relation.domain(), line)
    assert projection in Mor(modules)(line, quotient)

    # Left-module matrix coefficients act on the right of source coefficients.
    assert ask(relation(line.point(e12)) == line.zero()) is True
    assert ask(relation(line.point(e21)) == line.point(e21)) is True

    respecting = finite_free_matrix_morphism(modules, line, line, ((e22,),))
    assert ask(respecting * relation == respecting * zero) is True
    factor = presented_module_factor(modules, quotient, line, respecting)
    assert factor in Mor(modules)(quotient, line)
    assert factor is not respecting
    assert ask(factor * projection == respecting) is True
    assert ask(factor(projection(line.point(e22.datum()))) == line.point(e22.datum())) is True


test_unified_module_api_preserves_noncommutative_scalars_and_universal_factor()
