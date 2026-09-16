"""Scalar-general finite module presentations retain their module coequalizer."""

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
from sage_categories.algebra.free_modules import (
    finite_free_matrix_morphism,
    ordinary_modules,
)
from sage_categories.algebra.presented_modules import (
    finitely_presented_module,
    presented_module_diagram,
    presented_module_factor,
    presented_module_presentation,
    presented_module_projection,
    presented_module_relation,
    presented_module_zero,
)
from sage_categories.cat.category import ask
from sage_categories.cat.cones import cocone, cocones
from sage_categories.cat.functors import Cat
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import Monoids


def matrix_ring():
    """``M_2(F_2)`` in row-major order as a monoid object of ``(Ab, tensor)``."""
    engine = AdditiveAbelianGroup([2, 2, 2, 2])
    entries = lambda datum: [int(c) for c in datum.vector()]
    element = lambda values: engine.linear_combination_of_smith_form_gens(vector(ZZ, values))

    def multiply(a, b):
        x, y = entries(a), entries(b)
        return element([
            x[0] * y[0] + x[1] * y[2],
            x[0] * y[1] + x[1] * y[3],
            x[2] * y[0] + x[3] * y[2],
            x[2] * y[1] + x[3] * y[3],
        ])

    group = presented_abelian_group(engine)
    one = element([1, 0, 0, 1])
    ring = Monoids(AbelianTensor())(
        tensor_mediator(group, group, group, multiply),
        abelian_homomorphism(integer_group(), group, lambda k: k * one),
    )
    return element, group, ring


def test_noncommutative_relation_retains_exact_module_coequalizer_and_factor() -> None:
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
    diagram = presented_module_diagram(modules, quotient)
    universal = presented_module_presentation(modules, quotient)
    line = relation.codomain()

    assert quotient in modules
    assert modules.scalars() is ring
    assert relation in Mor(modules)(relation.domain(), line)
    assert zero in Mor(modules)(relation.domain(), line)
    assert projection in Mor(modules)(line, quotient)
    assert universal.apex() is quotient
    assert universal.diagram() is diagram
    assert universal.leg(Cat().WalkingParallelPair()(1)) is projection
    assert ask(projection * relation == projection * zero) is True

    # For a left module the matrix coefficient is on the right.  Thus the relation
    # r |-> r E11 kills E12 but fixes E21; the reversed convention does the opposite.
    assert ask(relation(line.point(e12)) == line.zero()) is True
    assert ask(relation(line.point(e21)) == line.point(e21)) is True

    respecting = finite_free_matrix_morphism(modules, line, line, ((e22,),))
    assert ask(respecting * relation == respecting * zero) is True
    factor = presented_module_factor(modules, quotient, line, respecting)
    assert factor in Mor(modules)(quotient, line)
    assert ask(factor * projection == respecting) is True
    assert ask(factor(projection(line.point(e22.datum()))) == line.point(e22.datum())) is True

    shape = diagram.domain()
    source_vertex = shape(0)

    def candidate_leg(vertex):
        match vertex is source_vertex:
            case True:
                return respecting * relation
            case False:
                return respecting

    generic_factor = universal.lift(cocones(diagram)(cocone(diagram, line, candidate_leg)))
    assert ask(generic_factor == factor) is True

    non_respecting = finite_free_matrix_morphism(modules, line, line, ((e11,),))
    assert ask(non_respecting * relation == non_respecting * zero) is False
    try:
        presented_module_factor(modules, quotient, line, non_respecting)
    except AssertionError as error:
        assert "does not respect" in str(error)
    else:
        raise AssertionError("a map that violates the relation must not factor")


test_noncommutative_relation_retains_exact_module_coequalizer_and_factor()
