"""Scalar-general finite free modules are owned module biproducts/direct sums."""

from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ

from sage_categories.algebra.abelian import (
    AbelianTensor,
    abelian_homomorphism,
    integer_group,
    presented_abelian_group,
    simple_tensor,
    tensor_mediator,
)
from sage_categories.algebra.free_modules import (
    finite_free_basis,
    finite_free_basis_family,
    finite_free_injection,
    finite_free_matrix_morphism,
    finite_free_module,
    finite_free_projection,
    free_module_homomorphism,
    ordinary_modules,
    regular_module,
)
from sage_categories.cat.category import ask
from sage_categories.cat.monoidal import SelfAction
from sage_categories.cat.structured_objects import Monoids


def matrix_ring():
    """``M_2(F_2)`` in row-major entry order, as a monoid object of ``(Ab, tensor)``."""
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


def test_finite_free_module_retains_basis_product_coproduct_and_left_action() -> None:
    element, group, ring = matrix_ring()
    modules = ordinary_modules(ring)
    assert modules.scalars() is ring
    assert modules.actegory() is SelfAction(AbelianTensor())

    regular = regular_module(modules)
    zero_free = finite_free_module(modules, 0)
    zero_family = finite_free_basis_family(modules, zero_free)
    assert tuple(finite_free_basis(modules, zero_free)) == ()
    assert modules.Limits(zero_family.domain()).universal_data(zero_family).apex() is zero_free
    assert modules.Colimits(zero_family.domain()).universal_data(zero_family).apex() is zero_free
    zero_matrix = finite_free_matrix_morphism(modules, zero_free, zero_free, ())
    assert zero_matrix.domain() is zero_free and zero_matrix.codomain() is zero_free

    free = finite_free_module(modules, 2)
    assert modules.forgetful().on_object(regular) is group
    assert free in modules

    basis = finite_free_basis(modules, free)
    family = finite_free_basis_family(modules, free)
    assert tuple(point.datum() for point in basis) == (0, 1)
    assert family.on_object(family.domain().object_at(basis.point(0))) is regular
    assert family.on_object(family.domain().object_at(basis.point(1))) is regular
    assert modules.Limits(family.domain()).universal_data(family).apex() is free
    assert modules.Colimits(family.domain()).universal_data(family).apex() is free

    first, second = basis.point(0), basis.point(1)
    include_first = finite_free_injection(modules, free, first)
    include_second = finite_free_injection(modules, free, second)
    project_first = finite_free_projection(modules, free, first)
    project_second = finite_free_projection(modules, free, second)
    assert include_first.domain() is regular and include_first.codomain() is free
    assert include_second.domain() is regular and include_second.codomain() is free
    assert project_first.domain() is free and project_first.codomain() is regular
    assert project_second.domain() is free and project_second.codomain() is regular

    def swap_basis(index):
        return include_second if index is first else include_first

    swap = free_module_homomorphism(modules, free, free, swap_basis)
    assert ask(swap * include_first == include_second) is True
    assert ask(swap * include_second == include_first) is True

    e12 = element([0, 1, 0, 0])
    e21 = element([0, 0, 1, 0])
    e11 = element([1, 0, 0, 0])
    e22 = element([0, 0, 0, 1])
    underlying = modules.forgetful().on_object(free)
    underlying_injection = modules.forgetful().on_morphism(include_first)
    vector_in_first_summand = underlying_injection(group.point(e21))
    scaled = free.action()(simple_tensor(group, underlying, e12, vector_in_first_summand.datum()))
    expected = underlying_injection(group.point(e11))
    wrong_right_action = underlying_injection(group.point(e22))
    # The module action is left multiplication: E12 E21 = E11, whereas reversing
    # the scalar side would give E21 E12 = E22.
    assert ask(scaled == expected) is True
    assert ask(scaled == wrong_right_action) is False


def test_matrix_is_only_the_chosen_basis_specialization_of_a_free_map() -> None:
    element, group, ring = matrix_ring()
    modules = ordinary_modules(ring)
    line = finite_free_module(modules, 1)
    e12 = group.point(element([0, 1, 0, 0]))
    e21 = element([0, 0, 1, 0])
    e11 = element([1, 0, 0, 0])
    e22 = element([0, 0, 0, 1])

    mapping = finite_free_matrix_morphism(modules, line, line, ((e12,),))
    assert mapping.domain() is line and mapping.codomain() is line
    image = mapping(line.point(e21))
    # For left modules the chosen-basis coefficient is on the right:
    # E21 |-> E21 E12 = E22, not E12 E21 = E11.
    assert ask(image == line.point(e22)) is True
    assert ask(image == line.point(e11)) is False


test_finite_free_module_retains_basis_product_coproduct_and_left_action()
test_matrix_is_only_the_chosen_basis_specialization_of_a_free_map()
