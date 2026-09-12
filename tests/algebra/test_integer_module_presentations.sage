"""Finite matrix module presentations use the existing ZZ-module and CAP cokernel owners."""

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup

from sage_categories.all import Mor, ask
from sage_categories.algebra import (
    AbelianGroups,
    abelian_homomorphism,
    integer_module,
    presented_abelian_group,
    presented_integer_module,
)


def test_relation_matrix_retains_cokernel_and_nonidentity_universal_factor() -> None:
    presentation = presented_integer_module(((2,),))
    target_free = presentation.target_free_module()
    relation = presentation.relation_morphism()
    projection = presentation.cokernel_projection()
    generator = presentation.target_basis_element(0)

    assert tuple(tuple(int(entry) for entry in row) for row in presentation.relation_matrix().rows()) == ((2,),)
    assert relation.domain() is presentation.source_free_module()
    assert relation.codomain() is target_free
    assert projection.domain() is target_free
    assert projection.codomain() is presentation.module()
    quotient_generator = projection(generator)
    assert ask(quotient_generator + quotient_generator == presentation.module().zero()) is True

    four_engine = AdditiveAbelianGroup([4])
    four_group = presented_abelian_group(four_engine)
    four = integer_module(four_group)
    modules = presentation.module_category()
    underlying_source = modules.forgetful().on_object(target_free)
    generator_four = four_engine.gen(0)
    to_four = abelian_homomorphism(
        underlying_source,
        four_group,
        lambda value: int(value.vector()[0]) * 2 * generator_four,
    )
    coequalizing = modules.homomorphism(target_free, four, to_four)
    factor = presentation.factor(four, coequalizing)

    assert factor in Mor(modules)(presentation.module(), four)
    assert ask(factor(quotient_generator) == four.point(2 * generator_four)) is True
    assert ask(factor * projection == coequalizing) is True


def test_noncommutative_scalar_module_remains_a_separate_supported_action() -> None:
    # The noncommutative M_2(F_2) specimen lives in test_matrix_ring_scaffold.sage;
    # this assertion pins that finite matrix presentations do not redefine Modules.
    presentation = presented_integer_module(((3, 0), (0, 5)))
    modules = presentation.module_category()
    assert presentation.module() in modules
    assert modules.forgetful().on_object(presentation.module()) in AbelianGroups()


test_relation_matrix_retains_cokernel_and_nonidentity_universal_factor()
test_noncommutative_scalar_module_remains_a_separate_supported_action()
