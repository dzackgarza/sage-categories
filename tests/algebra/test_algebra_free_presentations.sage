"""Free algebra relations are retained as actual algebra coequalizers."""

from sage_categories.algebra.abelian import AbelianBimoduleTensor
from sage_categories.algebra.algebras import Algebras
from sage_categories.algebra.free_associative import (
    free_associative_coefficients,
    free_associative_element,
    free_associative_product,
)
from sage_categories.algebra.indexed_modules import integer_scalar_monoid
from sage_categories.algebra.presented_algebras import (
    integer_free_algebra,
    integer_free_algebra_generator,
    integer_free_algebra_homomorphism,
    presented_algebra_diagram,
    presented_algebra_factor,
    presented_algebra_presentation,
    presented_algebra_projection,
    retain_split_algebra_presentation,
)
from sage_categories.cat.category import ask
from sage_categories.cat.morphisms import Mor


def test_polynomial_elimination_relation_retains_algebra_coequalizer() -> None:
    r"""``ZZ<x,y>/(y-x^2) = ZZ[x]`` with its actual universal evaluation map."""
    scalars = integer_scalar_monoid()
    algebras = Algebras(scalars, AbelianBimoduleTensor(scalars))
    free = integer_free_algebra(algebras, ("x", "y"))
    relations = integer_free_algebra(algebras, ("r",))
    quotient = integer_free_algebra(algebras, ("x",))

    x = integer_free_algebra_generator(algebras, free, 0)
    y = integer_free_algebra_generator(algebras, free, 1)
    qx = integer_free_algebra_generator(algebras, quotient, 0)
    free_neutral = algebras.monoid_presentation().on_object(free)
    quotient_neutral = algebras.monoid_presentation().on_object(quotient)
    x_squared = free_associative_product(free_neutral, x, x)
    qx_squared = free_associative_product(quotient_neutral, qx, qx)

    relation = integer_free_algebra_homomorphism(
        algebras,
        relations,
        free,
        (y,),
    )
    polynomial = integer_free_algebra_homomorphism(
        algebras,
        relations,
        free,
        (x_squared,),
    )
    projection = integer_free_algebra_homomorphism(
        algebras,
        free,
        quotient,
        (qx, qx_squared),
    )
    section = integer_free_algebra_homomorphism(
        algebras,
        quotient,
        free,
        (x,),
    )
    presented = retain_split_algebra_presentation(
        algebras,
        relation,
        polynomial,
        projection,
        section,
    )

    assert presented is quotient
    assert presented_algebra_projection(algebras, quotient) is projection
    presentation = presented_algebra_presentation(algebras, quotient)
    diagram = presented_algebra_diagram(algebras, quotient)
    assert presentation.diagram() is diagram
    assert ask(projection * relation == projection * polynomial) is True

    # A relation-respecting generator assignment factors through ZZ[x].  The
    # factor is genuinely between different free-algebra objects, not an identity.
    target = integer_free_algebra(algebras, ("z",))
    z = integer_free_algebra_generator(algebras, target, 0)
    target_neutral = algebras.monoid_presentation().on_object(target)
    z_squared = free_associative_product(target_neutral, z, z)
    respecting = integer_free_algebra_homomorphism(
        algebras,
        free,
        target,
        (z, z_squared),
    )
    factor = presented_algebra_factor(algebras, quotient, target, respecting)
    assert factor.domain() is quotient and factor.codomain() is target
    assert ask(factor * projection == respecting) is True
    underlying_factor = algebras.to_modules().on_morphism(factor)
    assert ask(underlying_factor(qx) == z) is True

    # The identity assignment violates y=x^2 and therefore cannot define the
    # quotient factor.
    violating = Mor(algebras)(free, free).one()
    assert ask(violating * relation == violating * polynomial) is False
    try:
        presented_algebra_factor(algebras, quotient, free, violating)
    except AssertionError:
        pass
    else:
        raise AssertionError("a generator assignment violating y=x^2 must not factor")

    # The quotient is the one-generator polynomial algebra ZZ[x], whose underlying
    # module still contains every finite-degree monomial.  No span of the algebra
    # generator is substituted for the full module.
    module = algebras.to_modules().on_object(quotient)
    long_word = (0,) * 101
    long_element = free_associative_element(quotient_neutral, {long_word: 3})
    assert long_element.parent() is module
    assert free_associative_coefficients(quotient_neutral, long_element) == {
        long_word: 3
    }
    x_squared_again = free_associative_product(quotient_neutral, qx, qx)
    x_cubed = free_associative_product(quotient_neutral, x_squared_again, qx)
    assert (
        ask(
            free_associative_product(quotient_neutral, x_squared_again, x_cubed)
            == free_associative_product(quotient_neutral, x_cubed, x_squared_again)
        )
        is True
    )


test_polynomial_elimination_relation_retains_algebra_coequalizer()
